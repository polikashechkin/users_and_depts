import os, json, sys
from . import Page as BasePage
from . import Button, Input, Title, Toolbar, Select

from domino.core import log
from domino.tables.account_db.database import Database
from domino.tables.postgres.dept import Dept
import cx_Oracle
 
class Page(BasePage):
    def __init__(self, application, request):
        super().__init__(application, request)
        self.postgres = None
        self.account_db = None
        self.database_id = self.attribute('database_id')

    def add_database(self):
        try:
            dept = self.postgres.query(Dept).get(self.get('dept_id'))
            database = Database(account_id = self.account_id, database_id = dept.guid)
            database.host = self.get('host')
            database.port = int(self.get('port'))
            database.service_name = self.get('service_name')
            database.scheme = self.get('user_name')
            self.account_db.add(database)
            self.account_db.commit()
            self.message(f'{database.dsn}@{database.user_name}')
        except Exception as ex:
            log.exception(__file__)
            self.error(ex)
            raise Exception(ex)

    def __call__(self):
        Title(self, f'Добавить базу данных')
        database = self.account_db.query(Database).get((self.account_id, Database.BASE_DATABASE))
        toolbar = Toolbar(self, 'toolbar')
        select = Select(toolbar.item(mr=0.5), label='Подразделение', name='dept_id')
        for dept in self.postgres.query(Dept).filter(Dept.guid != None):
            select.option(dept.id,dept.name)
        Input(toolbar.item(mr=0.5), label='host', name='host', value=database.host)
        Input(toolbar.item(mr=0.5), label='port', name='port', value=database.port)
        Input(toolbar.item(mr=0.5), label='service_name', name='service_name', value=database.service_name)
        Input(toolbar.item(mr=0.5), label='user_name', name='user_name', value=database.user_name)

        actions = Toolbar(self, 'actions').mt(1)
        Button(actions, 'Добавить базу данных').onclick('.add_database', forms=[toolbar])

        
        


