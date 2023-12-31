import uvicorn
import getpass
import subprocess
import time
import sys

from app.config import settings



def systemctl_ready_check(service: str) -> bool:
    ready_check = "Active: active (running)"
    proc = subprocess.run(f"systemctl status {service}", shell=True, check=False, capture_output=True)
    status = proc.stdout.decode()
    if ready_check in status:
        return True
    return False

def process_ready_check(proc: str) -> bool:
    proc = subprocess.run(f"pidof {proc}", shell=True, check=False, capture_output=True)
    status = proc.stdout.decode()
    if status:
        return True
    return False

def restart_systemctl(services: list[str]=['postgresql', 'redis']):
    password = None
    for service in services:
        if systemctl_ready_check(service):
            print(f'{service} already started')
        else:
            if not password:
                password = getpass.getpass(f'Enter your sudo password (launching {services})->:')
            proc = subprocess.Popen(f"sudo -S systemctl restart {service}.service", shell=True, stdin=subprocess.PIPE)
            proc.communicate(password.encode())
            if systemctl_ready_check(service):
                print(f'\n{service} has started')
            else:
                raise Exception(f"{service} cant start")
    return password


def restart_celery():
    # cout = subprocess.Popen(f"poetry run celery -A app.tasks.celery:celery beat --loglevel=INFO", shell=True)
    # print('celery scheduling has started', cout)
    cout = subprocess.Popen(f"poetry run celery -A app.tasks.celery:celery worker --loglevel=INFO --beat", shell=True)
    print('celery workers has started', cout)
    time.sleep(5)
    cout = subprocess.Popen(f"poetry run celery -A app.tasks.celery:celery flower --loglevel=INFO", shell=True)
    print('celery monitoring has started', cout)


def restart_server():
    uvicorn.run("app.main:app",
                host=settings.APP_HOST,
                port=settings.APP_PORT,
                proxy_headers=True,
                forwarded_allow_ips='*',
                reload=True)


def restart_nginx(password=None):
    if process_ready_check('nginx'):
        print('nginx already started')
    else:
        if not password:
            password = getpass.getpass(f'Enter your sudo password (launching nginx)->:')
        proc = subprocess.Popen('sudo -S /usr/bin/nginx -p . -c nginx.conf', shell=True, stdin=subprocess.PIPE)
        proc.communicate(password.encode())
        print("nginx has started")


if __name__ == "__main__":
    if not sys.argv[1:]:
        password = restart_systemctl(['postgresql', 'redis'])
        restart_nginx(password)
    else:
        password = None
    restart_celery()
    restart_server()
