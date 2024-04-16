from datetime import datetime
from glob import glob as gb
from zipfile import ZipFile
from icecream import ic
import aiohttp
import json
import sys
import os
import re
import warnings
warnings.filterwarnings('ignore')

from typing import List, Tuple
from loguru import logger
from fastapi import File
import pandas as pd

from app.rosreestr.query.repo import QueriesDAO, BalanceDAO, BalanceMonDAO
from app.rosreestr.query.order.repo import OrdersDAO
from app.rosreestr.monitoring.repo import MonitoringsDAO
from app.users.repo import UsersDAO
from app.rosreestr.query.order.models import Orders
from app.rosreestr.schemas import SDownload, SQuery
from app.rosreestr.monitoring.schemas import SOrderMon
from app.users.models import Users # need for celery detection
from app.config import settings
sys.path.append(settings.RR_API_LIB_PATH)
from kr import Queries as kr_connector


class Utility:
    if settings.MODE == 'TEST':
        api_key = settings.TEST_RR_KR_API_KEY
        org_id  = settings.TEST_RR_KR_ORG_ID
    else:
        api_key = settings.RR_KR_API_KEY
        org_id  = settings.RR_KR_ORG_ID

    tg_channel = settings.TG_RR_CHANNEL_ID
    tg_bot = settings.TG_BOT_TOKEN
    session = kr_connector(api_key=api_key,
                           org_id=org_id,
                           logger=logger,
                           dir_path=settings.RR_STORAGE,
                           url_type=settings.MODE,
                          )


    @classmethod
    async def create_orders_by_txt(cls, query: SQuery, user_id: int) -> int:
        project = cls.session.get_project(query.project)
        query_id = await QueriesDAO.add(project=project, user_id=user_id)
        query_s = [('simple',  cad) for cad in query.query_s.split('\n')] if query.query_s else []
        query_h = [('history', cad) for cad in query.query_h.split('\n')] if query.query_h else []
        for order in query_s + query_h:
            cadastral = cls.session.cadastral_verify(order[1])
            if not cadastral:
                continue
            cadastral_type = order[0]
            await OrdersDAO.add(
                id=cls.session.get_uid(t='uid'),
                query_id=query_id,
                cadastral=cadastral,
                cadastral_type=cadastral_type,
                status='New',
                created_at=datetime.now(),
                modified_at=datetime.now(),
            )
            logger.info(f"rr.utility::{project}_{cadastral}_{cadastral_type} добавлен в БД")
        return query_id


    # @classmethod
    # async def create_orders_by_xls(cls, file: File):
    #     pass


    @classmethod
    async def query_orders(cls, query_id: int | None = None):
        """
        for celery
        """
        if query_id:
            orders = await OrdersDAO.find_all(query_id=query_id, status='New')
        else:
            orders = await OrdersDAO.find_all(status='New')
        for order in orders if orders else ():
            result = await cls.session.create(order.id, order.cadastral, order.cadastral_type)
            await OrdersDAO.update(
                item_id=order.id,
                session_id=result['session_id'],
                status=str(result['status']),
                status_txt=str(result['status_txt']),
                created_at=datetime.strptime(result['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ'),
                modified_at=datetime.strptime(result['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ'),
            )


    @classmethod
    async def check_orders(cls, query_id=None):
        """
        без аргумента - for celery
        с аргументом  - проверить и скачать все по query_id
        """
        if query_id:
            orders = await OrdersDAO.find_all(query_id=int(query_id))
        else:
            orders = await OrdersDAO.get_all_unready()
        for order in orders if orders else ():
            result = await cls.session.check(
                session_id=order.session_id,
                cadastral=order.cadastral,
                o_type=order.cadastral_type,
            )
            await OrdersDAO.update(
                item_id=order.id,
                status=str(result['new_status']),
                status_txt=str(result['new_status_txt']),
                modified_at=result['modified_at'],
            )

            project = await QueriesDAO.get_name(query_id=order.query_id)
            if result['new_status'] == 'Processed':
                await cls.session.download(
                    project=project,
                    file_data=result['file']
                )
                cls._xls_converter(
                    data=result['file'],
                    project=project,
                    cadastral=order.cadastral,
                    cadastral_type=order.cadastral_type,
                )
                await OrdersDAO.update(
                    item_id=order.id,
                    is_ready=True,
                )

            if not query_id and await QueriesDAO.is_all_ready(query_id=order.query_id):
                cls._analyze(project)
                cls._zipping(project)
                await QueriesDAO.update(item_id=order.query_id, is_ready=True)
                query = await QueriesDAO.find_by_id(model_id=order.query_id)
                user = await UsersDAO.find_by_id(model_id=query['user_id'])
                message = f"{user['username'] if user else ''}, заказ <{project}> готов"
                await cls._telegram_send_to_channel(message)

        if query_id:
            project = await QueriesDAO.get_name(query_id=order.query_id)
            cls._analyze(project)
            cls._zipping(project)
            message = f"заказ <{project}> готов"
            await cls._telegram_send_to_channel(message)


    @classmethod
    async def _telegram_send_to_channel(cls, text: str):
        URL = f'https://api.telegram.org/bot{cls.tg_bot}/sendMessage?chat_id={cls.tg_channel}&text={text}'
        async with aiohttp.ClientSession(trust_env=True) as a_session:
            async with a_session.post(url=URL) as resp:
                response = await resp.json()
                if resp.ok:
                    logger.info(f"rr.utility::сообщение отправлено в TG_{text}")
                else:
                    logger.error(f"rr.utility::сообщение НЕ отправлено в TG ({text})_{response}")


    @classmethod
    async def reorder(cls, query_id):
        orders = await OrdersDAO.find_all(query_id=int(query_id), status='Processing')
        for order in orders if orders else ():
            await OrdersDAO.add(
                id=cls.session.get_uid(t='uid'),
                query_id=query_id,
                cadastral=order.cadastral,
                cadastral_type=order.cadastral_type,
                status='New',
                created_at=datetime.now(),
                modified_at=datetime.now(),
            )
            logger.info(f"rr.utility::{order.cadastral}_{order.cadastral_type} добавлен в БД")



    @classmethod
    async def find(cls, query: str):
        return await cls.session.search(query)


    @classmethod
    async def prepare_for_download(cls, query_id: int, query_name: str):
        query = await QueriesDAO.find_by_id(query_id)
        if query and query['is_ready']:
            return
        cls._analyze(query_name)
        cls._zipping(query_name)


    @classmethod
    def _xls_converter(cls,
              data:           dict,
              project:        str,
              cadastral:      str,
              cadastral_type: str):
        def flatten_json(y):
            out = {}

            def flatten(x, name=''):
                if type(x) is dict:
                    for a in x:
                        flatten(x[a], name + a + '_')
                elif type(x) is list:
                    i = 0
                    for a in x:
                        flatten(a, name + str(i) + '_')
                        i += 1
                else:
                    out[name[:-1]] = x

            flatten(y)
            return out

        try:
            # делаем плоской и загоняем в df
            data = flatten_json(data)
            # DICT = flatten_json(DICTIONARY)
            df = pd.DataFrame.from_dict(data, orient='index').T  # полностью плоский df
            # df = pd.json_normalize(data)  # внутри есть списки со словарями
            df = df.reset_index(drop=True)
            # переводим лишние колонки в строки
            ## определяем эти лишние колонки (содержат цифру)
            cols_digit = []
            for i in df.columns:
                digits_in = re.findall(r'\d+', i)
                if re.findall(r'\d+', i) and not 'extract' in i:
                    cols_digit.append((digits_in, i))
            ## делаем строки из этих колонок
            for digit, col in cols_digit:
                d = int(digit[0])
                c = '_'.join(col.split(f"_{digit[0]}_"))
                df.loc[d, c] = df.loc[0, col]
            ## удаляем изначальные строки
            cols_to_save = df.columns.tolist()
            for i, col in cols_digit:
                cols_to_save.remove(col)
            for col in df.columns.tolist():
                if 'extract' in col:
                    cols_to_save.remove(col)
            logger.info(f"rr.utility::{project}_{cadastral}_{cadastral_type} распарсен")

            name = f'{"-".join(cadastral.split(":"))}_{cadastral_type}.xlsx'
            file_name = f'{cls.session.dir_path}/{project}/{name}'
            df[cols_to_save].to_excel(file_name)
            logger.info(f"rr.utility::{project}_{cadastral}_{cadastral_type} сохранен")
        except Exception as e:
            logger.error(f"rr.utility::{project}_{cadastral}_{cadastral_type} распарсить / сохранить не получилось!")
            print(e)

    @classmethod
    def _zipping(cls, project: str):
        paths = f'{cls.session.dir_path}/{project}/'
        zip_files = gb(paths + '*.zip')
        for zip_file in zip_files:
            folder = '/'.join(zip_file.split('/')[:-1]) + '/'
            name = zip_file.split('/')[-1][:-4] + '.pdf'
            with ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(folder)
                old_name = zip_ref.namelist()[0]
            os.replace(folder+old_name, folder+name)
        pdf_files = gb(paths + '*.pdf')

        # компануем pdf и итоговый xlsx в итоговый zip
        zip_result = ZipFile(f'{cls.session.dir_path}/{project}.zip', 'w')
        for pdf_file in pdf_files:
            zip_result.write(pdf_file, pdf_file.split('/')[-1])
        zip_result.write(f'{cls.session.dir_path}/{project}.xlsx', project+'.xlsx')
        zip_result.close()


    @classmethod
    def _analyze(cls, project):
        def clear_owner_col(col_name):
            return re.sub(r"_\d+_", '_', col_name.replace('rightMovements_', ''))

        def swap_list_values_by_index(lst, pos1, pos2):
            if pos2 != len(lst):
                lst[pos1], lst[pos2] = lst[pos2], lst[pos1]
            return lst

        def rus_localizaton(col):
            with open(f'app/rosreestr/localization.json', encoding='utf8') as file:
                ru_dict = json.load(file)
                return ru_dict[col] if col in ru_dict.keys() else col

        logger.debug(f'starting to concat excels of <{project}>')
        file_name = f'{cls.session.dir_path}/{project}'
        d_files = gb(f'{file_name}/*.xlsx')
        # if os.path.isfile(file_name + '.xlsx'):
            # file_name = f'{file_name}_{time.time_ns()}'
        df_s = pd.DataFrame()
        df_h = pd.DataFrame()
        for file in d_files:
            logger.debug(f'concating <{file}>')
            name = file.split('/')[-1]
            _df = pd.read_excel(file)
            if 'h' in name.split('.')[0]:
                df_h = pd.concat([df_h, _df], axis=0, ignore_index=True)
            else:
                df_s = pd.concat([df_s, _df], axis=0, ignore_index=True)

        # убираем лишние префиксы из названий
        df_s.columns = [col.replace('data_', '').replace('order', 'cadastral') \
                        for col in df_s.columns.to_list()]
        df_h.columns = [col.replace('data_', '').replace('order', 'cadastral') \
                        for col in df_h.columns.to_list()]

        # сразу сохраняем исходные данные
        writer = pd.ExcelWriter(file_name + '.xlsx', engine='xlsxwriter')
        df_s.to_excel(writer, sheet_name='simple', header=True, index=False)
        df_h.to_excel(writer, sheet_name='history', header=True, index=False)
        logger.debug(f'concating <{project}> is finished')

        if not df_h.empty:
            try:
                # # Добавление в dataset данных исторических выписок
                logger.debug(f'History of <{project}> is adding to dataset list')
                cols = df_h.columns.tolist()
                owners_cols = [c for c in cols if 'owners' in c]
                indexes = df_h[df_h['Unnamed: 0'] == 0].index.tolist()
                o_ind = []  # это список из кортежей с индексами "от" и "до" по каждой выписке
                for i, j in enumerate(indexes):
                    if i != len(indexes)-1:
                        o_ind.append((j, indexes[i+1] - 1))
                    else:
                        o_ind.append((j, j))
                logger.debug(f'History of <{project}> is added to dataset list')

                # делаем чтобы каждый блок owners начинался с имени, чтобы потом проверять наличие записи везде по имени
                # по-умолчанию после сортировки получается, что имя либо первое, либо инн. Если инн - меняем местами
                owners_cols.sort()
                is_swapped = False
                for i, col in enumerate(owners_cols):
                    if 'inn' in col and not is_swapped:
                        owners_cols = swap_list_values_by_index(owners_cols,i,i+1)
                        is_swapped = True
                        continue
                    if is_swapped:
                        is_swapped = False

                logger.debug(f'Accumulating owners history data of <{project}> to dataset list')
                df = pd.DataFrame()
                for item in o_ind:  # по каждому объекту
                    print('|', end='')
                    shift = df.index[-1] - item[0] + 1 if not df.index.empty else 0  # сдвиг, если вставляем новые строчки
                    df.loc[item[0]+shift, 'cadastral'] = df_h.loc[item[0], 'cadastral']
                    df.loc[item[0]+shift, 'Выписка историческая'] = f'@ГИПЕРССЫЛКА("{df_h.loc[item[0], "cadastral"].replace(":","-")}_RealEstateOwnership.pdf";"историческая")'
                    df.loc[item[0]+shift, 'addressNotes'] = df_h.loc[item[0], 'addressNotes']
                    df.loc[item[0]+shift, 'estateType'] = df_h.loc[item[0], 'estateType']
                    #df.loc[item[0]+shift, 'area_value'] = df_h.loc[item[0], 'area_value']
                    #df.loc[item[0]+shift, 'area_unit'] = df_h.loc[item[0], 'area_unit']

                    for ind in range(item[0], item[1]+1):  # по каждому индексу объекта
                        for col in owners_cols:
                            if not pd.isna(df_h.loc[ind, col]):
                                if clear_owner_col(col) in df.columns and ind+shift in df.index and 'owners_name' in clear_owner_col(col) and not pd.isna(df.loc[ind+shift, clear_owner_col(col)]):
                                    shift += 1

                                df.loc[ind+shift, clear_owner_col(col)] = df_h.loc[ind, col]

                logger.debug(f'Accumulating owners history data of <{project}> to dataset list is completed')
                if not df_s.empty:
                    logger.debug(f'Simple data of <{project}> is adding to dataset list')
                    # # Добавление в dataset данных простых выписок
                    df_s['id'] = df_s['cadastral'] + df_s['owners_regNumber'].astype(str) + df_s['owners_name'].astype(str)
                    df['id'] = df['cadastral'] + df['owners_regNumber'].astype(str) + df['owners_name'].astype(str)
                    df['Выписка простая'] = df['Выписка историческая'].str.replace('Ownership', 'Info').replace('Историческая', 'Простая')
                    df_s.columns = [val if val != 'addressNotes' else 'Адрес' for val in df_s.columns.tolist()]
                    cols2merge = [item for item in df_s.columns.tolist() if item not in df_h.columns.tolist()]
                    cols2merge_obj = [col for col in cols2merge if not 'encumbrances' in col and not 'embedded' in col]
                    df = df.merge(df_s.loc[df_s['Адрес'].notnull(), \
                                        cols2merge_obj + ['cadastral']], how='left', on='cadastral').reset_index()

                    # делаем обременение одной строкой для merge
                    #cols2merge_encumbrances = [col for col in cols2merge if     'encumbrances' in col]
                    try:
                        df_s['Обременение'] = "За " + \
                            df_s['encumbrances_pledge_name'].fillna('').astype(str) + " ("+ \
                            df_s['encumbrances_pledge_inn'].fillna('').astype(str) + ") по " + \
                            df_s['encumbrances_document_name'].fillna('').astype(str) + " от " + \
                            df_s['encumbrances_document_issuerDate'].fillna('').astype(str)

                        df_s['Обременение'] = df_s['Обременение'].mask(df_s['Обременение'] == 'За  () по ')
                        d = pd.pivot_table(df_s[df_s['Обременение'].notnull()], index=['id'], values=['Обременение'], aggfunc=lambda x:list(x))
                        d['Обременение'] = d['Обременение'].astype(str)
                        # merging
                        df = df.merge(d, how='left', left_on='id_x', right_on='id')
                        del d
                    except Exception as e:
                        logger.error(e)

                    logger.debug(f'Simple data of <{project}> is added to dataset list')
                else:
                    logger.debug(f'Simple data about object of <{project}> cannot be added to dataset list because of simple data is not in query')

                # # Сортировка и причесывание данных --> сохранение
                logger.debug(f'Start to sort and beautify data of <{project}> at dataset list')
                try:
                    df.loc[df['owners_share_numerator'].notnull(), 'owners_share'] = df.loc[df['owners_share_numerator'].notnull(), 'owners_share_numerator'].astype(str) + ' / ' + \
                        df.loc[df['owners_share_numerator'].notnull(), 'owners_share_denominator'].astype(str)
                except Exception as e:
                    logger.error(e)
                try:
                    df.loc[(df['owners_regEndDate'].isnull()) & (df['owners_name'].notnull()), 'data_type'] = 'текущий'
                    df.loc[df['owners_regEndDate'].notnull(), 'data_type'] = 'исторический'
                except Exception as e:
                    logger.error(e)

                cols = df.columns.tolist()
                owners_col = [col for col in cols if 'owners' in col]
                encumbrances_col = [col for col in cols if 'encumbrances' in col]
                obj_col = [col for col in cols if not col in owners_col and not col in encumbrances_col]
                df.loc[df['cadastral'].notnull(), obj_col] = df.loc[df['cadastral'].notnull(), obj_col].fillna('-')
                df[obj_col] = df[obj_col].ffill()
                df = df[obj_col+owners_col+encumbrances_col]
                df.columns = [rus_localizaton(col) for col in df.columns.tolist()]
                df = df[[col for col in df.columns if not 'Del' in col and not 'index' in col]]
                df = df.drop_duplicates()
                df = df.sort_values(['Кадастровый номер', 'Дата регистрации права'], ascending=[True, False])

                df.to_excel(writer, sheet_name='dataset', header=True, index=False)
                logger.debug(f'Finished to sort and beautify data of <{project}> at dataset list')
            except Exception as e:
                logger.error("Cannot create <dataset> list:")
                logger.error(e)
        else:
            logger.debug(f'List dataset of <{project}> cant be done because of history is missing')
        writer.close()


    @classmethod
    async def add_mon(cls, query: SOrderMon, user_id: int):
        project = cls.session.get_project(query.project)
        for cadastral in query.monitoring_cadastral.split('\n'):
            cadastral = cls.session.cadastral_verify(cadastral)
            if not cadastral:
                continue
            await MonitoringsDAO.add(
                project=project,
                cadastral=cadastral,
                monitoring_intense=query.monitoring_intense if query.monitoring_intense >= 24 else 24,
                monitoring_duration=query.monitoring_duration,
                user_id=user_id
            )
            logger.info(f"rr.utility::{project}_{cadastral} добавлен в БД для мониторинга")


    @classmethod
    async def query_monitorings(cls):
        """
        for celery
        """
        orders = await MonitoringsDAO.find_all(status='New')
        for order in orders if orders else ():
            result = await cls.session.start_monitor(
                cadastral=order.cadastral,
                start_date=order.start_at,
                end_date=order.end_at,
                interval_h=order.interval
            )
            await MonitoringsDAO.update(
                item_id=order.id,
                status=str(result['status']),
                status_txt=str(result['status_txt']),
                monitoringId=str(result['monitoring_id']),
                modified_at=datetime.today(),
            )


    @classmethod
    async def check_monitorings(cls):
        """
        for celery
        """
        after_event_id = await MonitoringsDAO.get_last_event_id()
        last_event_id, events = await cls.session.check_monitor(after_event_id=after_event_id)
        await MonitoringsDAO.update_last_event_id(last_event_id)
        logger.info(f"rr.utility_mon::произошло {len(events)} событий в рамках мониторинга")
        for event in events:
            mon_mon_id = event['monitoringId']
            date = event['eventDate']
            state = event['state']
            mon_id = await MonitoringsDAO.get_id_from_mon_id(mon_mon_id)
            status_txt = ''
            if mon_id:
                if 'changes' in event.keys():
                    item = await MonitoringsDAO.find_by_id(mon_id)
                    if not item:
                        continue
                    user = await UsersDAO.find_by_id(model_id=item['user_id'])
                    messages = cls._mon_changes_dict_to_str(event['changes'])
                    message = f"{user['username'] if user else ''}, объект <{item['cadastral']}> проекта " + \
                              f"<{item['tag']}> изменился" + \
                              f": {messages[0] if messages[0] else 'изменения не отображены.'}"
                    status_txt = messages[1]
                    await cls._telegram_send_to_channel(message)
                    logger.info(f"rr.utility_mon::сообщение отправлено в TG по {item['tag']} - {item['cadastral']}")
                await MonitoringsDAO.update(
                    item_id=mon_id,
                    status=state,
                    status_txt=f"по состоянию на {date}" + status_txt
                )


    @classmethod
    def _mon_changes_dict_to_str(cls, changes: dict) -> Tuple[str, str]:
        message = ''
        status_txt = ''
        if 'oldValue' in changes.keys() and 'newValue' in changes.keys() and changes['oldValue'].keys() == changes['newValue'].keys():
            for key, old_value in changes['oldValue'].items():
                new_value = changes['newValue'][key]
                if old_value != new_value:
                    status_txt += f"\n- {key}: {str(old_value)} -> {str(new_value)}"
                    if key == 'area':
                        old_value = changes['oldValue'][key]['value']
                        new_value = changes['newValue'][key]['value']
                        message += f"\n- площадь изменилась с {str(old_value)} до {str(new_value)}."
                    elif key == 'owners':
                        message += f"\n- изменения в собственниках."
                    elif key == 'encumbrances':
                        message += f"\n- изменения в обременении."
        else:
            message = f""
            status_txt = "\n" + str(changes)
        return message, status_txt


    @classmethod
    async def del_monitoring(cls, cadastral):
        mon_id, mon_mon_id = await MonitoringsDAO.get_all_id(cadastral)
        await cls.session.stop_monitor(monitoringId=mon_mon_id)
        if mon_id:
            await MonitoringsDAO.delete(item_id=mon_id)


    @classmethod
    async def check_balance(cls):
        """
        for celery
        """
        balance = await cls.session.get_balance()
        if 'orders' in balance.keys():
            await BalanceDAO.add(balance['orders'])
        else:
            await BalanceDAO.add(0)
        if 'monitoring' in balance.keys():
            await BalanceMonDAO.add(balance['monitoring'])
        else:
            await BalanceMonDAO.add(0)
