from datetime import datetime
from glob import glob as gb
from zipfile import ZipFile
import asyncio
import json
import sys
import os
import re

from loguru import logger
from fastapi import File
import pandas as pd

from app.rosreestr.query.repo import QuariesDAO
from app.rosreestr.query.order.repo import OrdersDAO
from app.rosreestr.schemas import SQuery
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

    session = kr_connector(api_key=api_key,
                           org_id=org_id,
                           logger=logger,
                           url_type=settings.MODE,
                          )


    @classmethod
    async def create_orders_by_txt(cls, query: SQuery, user_id: int):
        project = cls.session.get_project(query.project)
        query_id = await QuariesDAO.add(project=project, user_id=user_id)
        for order in query.query_s.split(r'\r\n') if query.query_s else ():
            result = await cls.session.create(order, 'simple')
            await OrdersDAO.add(
                query_id=query_id,
                id=result['uid'],
                session_id=result['session_id'],
                cadastral=order,
                cadastral_type='simple',
                status=result['status'],
                status_txt=result['status_txt'],
                created_at=datetime.strptime(result['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ'),
                modified_at=datetime.strptime(result['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ'),
                )
        for order in query.query_h.split(r'\r\n') if query.query_h else ():
            result = await cls.session.create(order, 'history')
            await OrdersDAO.add(
                query_id=query_id,
                id=result['uid'],
                session_id=result['session_id'],
                cadastral=order,
                cadastral_type='history',
                status=result['status'],
                status_txt=result['status_txt'],
                created_at=datetime.strptime(result['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ'),
                modified_at=datetime.strptime(result['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ'),
                )


    # @classmethod
    # async def create_orders_by_xls(cls, file: File):
    #     pass


    @classmethod
    async def check_orders(cls):
        """
        for celery
        """
        orders = await OrdersDAO.get_all_unready()
        for order in orders:
            result = await cls.session.check(order.id)
            await OrdersDAO.modify(
                order_id=order.id,
                new_status=result['new_status'],
                new_status_txt=result['new_status_txt'],
                modified_at=result['modified_at'],
                )

            if result['new_status'] == 'processed':
                project = await QuariesDAO.get_name(query_id=order.query_id)
                await cls.session.download(project=query_id,
                                           file_data=result['file_data'])
                cls._xls_converter(
                    data=result['file_data'],
                    project=project,
                    cadastral=order.cadastral,
                    cadastral_type=order.cadastral_type,
                )


    def _xls_converter(self,
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
            file_name = self.session.path_dir + f'{project}/' + name
            df[cols_to_save].to_excel(file_name)
            logger.info(f"rr.utility::{project}_{cadastral}_{cadastral_type} сохранен")
        except:
            logger.error(f"rr.utility::{project}_{cadastral}_{cadastral_type} распарсить не получилось!")

    @classmethod
    def _zipping(cls, project:str):
        paths = f'{cls.session.dir_path}{project}/'
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
        zip_result = ZipFile(f'{cls.session.dir_path}{project}.zip', 'w')
        for pdf_file in pdf_files:
            zip_result.write(pdf_file, pdf_file.split('/')[-1])
        zip_result.write(f'{cls.session.dir_path}{project}.xlsx', project+'.xlsx')
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
        file_name = f'{cls.session.path_dir}{project}'
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
                            df_s['encumbrances_document_content'].fillna('').astype(str)
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
                logger.debug(f'Finished to sort and beautify data of <{str(projects)}> at dataset list')
            except Exception as e:
                logger.error("Cannot create <dataset> list:")
                logger.error(e)
        else:
            logger.debug(f'List dataset of <{str(projects)}> cant be done because of history is missing')
        writer.save()
