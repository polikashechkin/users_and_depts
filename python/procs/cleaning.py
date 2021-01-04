import os, sys, datetime, time, json, sqlite3
from sqlalchemy import delete, insert, select, update, text as T

#from lxml import etree

path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.append(path)

from domino.core import log, DOMINO_ROOT
from domino.jobs import Proc
from domino.databases.postgres import Postgres
#from domino.databases import Databases
from pages import Page as BasePage
from pages import Title, Text, Table, Toolbar, Select

from settings import MODULE_ID

from domino.tables.postgres.user import User
from domino.tables.postgres.dept import Dept, DeptTable
from domino.tables.postgres.dictionary import Dictionary, DictionaryTable
from domino.tables.postgres.request_log import RequestLog

DESCRIPTION = 'Реорганизация данных'
PROC_ID = 'procs/cleaning.py'

JOBS_AGE = 'jobs_age'
REQUEST_LOG_AGE = 'request_log_age'

def on_activate(account_id, msg_log):
    Proc.create(account_id, MODULE_ID, PROC_ID, description=DESCRIPTION, url='procs/cleaning')

class Page(BasePage):
    def __init__(self, application, request):
        super().__init__(application, request)
        self.proc = Proc.get(self.account_id, MODULE_ID, PROC_ID)

    def change_request_log_age(self):
        self.proc.info[REQUEST_LOG_AGE] = self.get(REQUEST_LOG_AGE)
        self.message(f'{self.proc.info[REQUEST_LOG_AGE]}')
        self.proc.save()

    def change_jobs_age(self):
        self.proc.info[JOBS_AGE] = self.get(JOBS_AGE)
        self.message(f'{self.proc.info[JOBS_AGE]}')
        self.proc.save()

    def __call__(self):
        Title(self, f'{self.proc.ID}, {DESCRIPTION}')
        Text(self).text('''
        Удаление данных, потерявших актуальность.
        ''')
        Text(self).mt(1).css('h5').text(f'''{os.path.join(DOMINO_ROOT,'uwsgi', 'uwsgi.log')}''')
        Text(self).text('''
        Данный файл содержит системные протоколы всех вызовов. Он необходим
        исключительно для целей отладки и выявления ошибок "online". Количество строк в данном файле 
        достаточно большое и он растет быстро. Нет никаких резонов сохранять его продолжительное время.
        При выполнении данной процедуры он обнуляется.
        ''')
        Text(self).css('h5').mt(1).text(os.path.join(DOMINO_ROOT, 'log', 'domino.log'))
        Text(self).text('''
        Данный файл содержит все непрогнозируемые ошибки исполнения и вся произвольная отладочная 
        информация. Он необходим исключительно для целей отладки и выявления ошибок "online". 
        Размер файла весьма большой и плохо прогнозируемый. Нет резонов сохранять его продолжительное время.
        При выполнении данной процедуры он обнуляется.
        ''')
        Text(self).css('h5').mt(1).text('Журналы вызовов')
        Text(self).mt(1).text('''
        Журналы вызовов организованы в виде некоторой базы данных (postgres). 
        В них сохраняется информация о "важных" http запросах и ответах. Это нужно для целей
        анализа взаимодействия между компонентами системы. Как правило, анализ проводится 
        через какое то время (не сразу). Поэтому данные следует какое то время хранить. Но не 
        слишком долго. Это определяется по текущей ситуации.
        ''')
        toolbar = Toolbar(self, 'log_request_age')
        select = Select(toolbar.item(), name=REQUEST_LOG_AGE, value=self.proc.info.get(REQUEST_LOG_AGE))
        select.option('', 'УДАЛЯТЬ ВСЕ ЗАПИСИ ПРИ ВЫПОЛНЕНИИ ДАННОЙ ПРОЦЕДУРЫ')
        select.option('2', 'УДАЛЯТЬ ВСЕ ЗАПИСИ, ЗА ИСКЛЮЧЕНИЕМ ПОСЛЕДНИХ 2-х ДНЕЙ')
        select.option('10', 'УДАЛЯТЬ ВСЕ ЗАПИСИ, ЗА ИСКЛЮЧЕНИЕМ ПОСЛЕДНИХ 10-ти ДНЕЙ')
        select.onchange('.change_request_log_age', forms=[toolbar])
        Text(self).css('h5').mt(1).text('Задачи/процедуры')
        Text(self).text('''
        В процессе выполнения процедур образуются рабочие наборы и протоколы исполнения.
        Они полезны для анализа выполнения процедур. Поскольку процедуры запускаются 
        в том числе и планировщиком, эти данные имеют актуальеность некоторое время.
        Объем данных относительно небльшой, но тем не менее хранить их долго тоже нет 
        никакого резона. Время хранения определяется по ситуации.
        ''')
        toolbar1 = Toolbar(self, 'jobs_age')
        select = Select(toolbar1.item(), name=JOBS_AGE, value=self.proc.info.get(JOBS_AGE))
        select.option('', 'НИКОГДА НЕ УДАЛЯТЬ ЭТИ ДАННЫЕ')
        select.option('30', 'УДАЛЯТЬ, ЗА ИСКЛЮЧЕНИЕМ ПОСЛЕДНИХ 30-ти ДНЕЙ')
        select.onchange('.change_jobs_age', forms=[toolbar1])

class Job(Proc.Job): 
    def __init__(self, ID):
        super().__init__(ID)
        self.postgres = None

    def __call__(self):
        self.proc = Proc.get(self.account_id, MODULE_ID, PROC_ID)
        self.log('НАЧАЛО РАБОТЫ')
        stop_reason = ''
        self.postgres = Postgres().session(self.account_id)
        try:
            self.dowork()
            self.postgres.commit()
        except BaseException as ex:
            log.exception(__file__)
            self.postgres.rollback()
            stop_reason = f'{ex}'
            raise Exception(stop_reason)
        finally:
            self.postgres.close()
        self.log(f'ОКОНЧАНИЕ РАБОТЫ {stop_reason}')
    
    def clean_logs(self):
        domino_log = os.path.join(DOMINO_ROOT, 'log', 'domino.log')
        self.log(f'ОЧИСТКА "{domino_log}"')
        with open(domino_log, 'w') as f:
            f.write(f'{datetime.datetime.now()}\n\n')
        uwsgi_log = os.path.join(DOMINO_ROOT, 'uwsgi', 'uwsgi.log')
        self.log(f'ОЧИСТКА "{uwsgi_log}"')
        with open(uwsgi_log, 'w') as f:
            f.write(f'{datetime.datetime.now()}\n\n')

    def clean_jobs(self):
        date = datetime.date.today()
        if self.jobs_age:
            age  = datetime.timedelta(days=int(self.jobs_age))
            date = datetime.date.today() - age
        self.log(f'Удаление задач, завершенных до {date}'.upper())

        sql = f'''
        select j.id 
        from proc_jobs as j join procs as p on j.proc_id = j.id
        where j.start_date < '{date}' and p.account_id = '{self.account_id}' and j.state > 1
        '''
        sql = sql.replace('\n', ' ')
        self.log(sql)
        jobs = []
        with sqlite3.connect(os.path.join(DOMINO_ROOT, 'data', 'jobs.db')) as conn:
            cur = conn.cursor()
            cur.execute(sql)
            for job_id, in cur.fetchall():
                jobs.append(job_id)
        self.log(f'{jobs}')

    def clean_reports(self):
        pass

    def clean_request_logs(self):
        query = self.postgres.query(RequestLog.id)
        if self.request_log_age:
            date = datetime.datetime.now()
            date -= datetime.timedelta(int(self.request_log_age))
            query = query.filter(RequestLog.ctime < date)
        query.delete()
        self.postgres.commit()
        self.log(f'ОЧИСТКА ЖУРНАЛОВ ВЫЗОВОВ')
        sql = f'{query}'.replace("\n", " ")
        self.log(f'{sql}')

    def dowork(self):
        self.request_log_age = self.info.get(REQUEST_LOG_AGE)
        self.jobs_age = self.info.get(JOBS_AGE)
        self.log(f'request_log_age={self.request_log_age}, jobs_age={self.jobs_age}')
        self.clean_logs()
        self.clean_request_logs()
        self.clean_jobs()

if __name__ == "__main__":
    try:
        with Job(sys.argv[1]) as job:
            job()
    except:
        log.exception(__file__)
    