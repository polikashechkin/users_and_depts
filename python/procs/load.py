import os, sys, datetime, time, json, sqlite3
from sqlalchemy import delete, insert, select, update, text as T

#from lxml import etree

path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.append(path)

from domino.core import log, DOMINO_ROOT
from domino.jobs import Proc
from domino.databases.postgres import Postgres
from domino.databases.oracle import Oracle
from pages import Page as BasePage
from pages import Title, Text, Table

from settings import MODULE_ID

from domino.tables.postgres.user import User

DESCRIPTION = 'Загрузка справочника пользователей'
PROC_ID = 'procs/load.py'

def on_activate(account_id, msg_log):
    Proc.create(account_id, MODULE_ID, PROC_ID, description=DESCRIPTION, url='None')

class Job(Proc.Job): 
    def __init__(self, ID):
        super().__init__(ID)

    def __call__(self):
        self.proc = Proc.get(self.account_id, MODULE_ID, PROC_ID)
        self.log('НАЧАЛО РАБОТЫ')

        #database = Databases().get_database(self.account_id)
        #self.db_connection = database.connect()
        #self.db_cursor = self.db_connection.cursor()

        #self.pg_session = Postgres.session(self.account_id)
        #self.pg_connection = Postgres.connect(self.account_id)
        #self.pg_connection.set_session(readonly=False, autocommit=True)
        #self.pg_cursor = self.pg_connection.cursor()

        stop_reason = ''
        self.postgres = Postgres.Pool().session(self.account_id)
        self.oracle = Oracle.Pool().session(self.account_id)
        try:
            self.dowork()
            self.postgres.commit()
        except BaseException as ex:
            log.exception(__file__)
            self.postgres.rollback()
            stop_reason = f'{ex}'
        finally:
            self.postgres.close()
            self.oracle.close()

        self.log(f'ОКОНЧАНИЕ РАБОТЫ {stop_reason}')
    
    def dowork(self):
        self.load_users()

    def load_users(self):
        self.log(f'ЗАГРУЗКА ПОЛЬЗОВАТЕЛЕЙ')
        sql = 'select id, domino.DominoUIDToString(id), name, full_name from domino_user where CLASS = 1 and TYPE=1 and name is not null'
        count = 0
        for UID, ID, NAME, FULL_NAME in self.oracle.execute(T(sql)):
            NAME = NAME.strip()
            user = self.postgres.query(User).get(ID)
            if user:
                user.name = NAME
                user.full_name = FULL_NAME
                user.uid = UID
            else:
                user = User(id=ID, name=NAME, full_name = FULL_NAME, uid=UID)
                self.postgres.add(user)
            count += 1
        self.log(f'Обработано {count} пользователей')
        self.postgres.commit()


if __name__ == "__main__":
    try:
        with Job(sys.argv[1]) as job:
            job()
    except:
        log.exception(__file__)
    