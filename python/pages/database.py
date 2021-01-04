import os, json, sys
from . import Page as BasePage
from . import Button, Input, Title, Toolbar
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

    def change_params(self):
        database = self.account_db.query(Database).get((self.account_id, self.database_id))
        database.host = self.get('host')
        database.port = int(self.get('port'))
        database.service_name = self.get('service_name')
        database.scheme = self.get('user_name')
        self.message(f'{database.dsn}@{database.user_name}')

    def __call__(self):
        database = self.account_db.query(Database).get((self.account_id, self.database_id))
        if database.database_id:
            dept = self.postgres.query(Dept).filter(Dept.guid == self.database_id).first()
            Title(self, f'{dept.name if dept else "Неизвестное подразделение"}')
        else:
            Title(self, f'Основная база данных')
        toolbar = Toolbar(self, 'toolbar')
        Input(toolbar.item(mr=0.5), label='host', name='host', value=database.host)
        Input(toolbar.item(mr=0.5), label='port', name='port', value=database.port)
        Input(toolbar.item(mr=0.5), label='service_name', name='service_name', value=database.service_name)
        Input(toolbar.item(mr=0.5), label='user_name', name='user_name', value=database.user_name)

        actions = Toolbar(self, 'actions').mt(1)
        Button(actions, 'Изменить').onclick('.change_params', forms=[toolbar])

        
        


