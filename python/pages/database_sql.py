import os, json, sys
from . import Page as BasePage
from . import Button, Input, Title, Toolbar, InputText, Table
from domino.core import log
from domino.tables.account_db.database import Database
from domino.tables.postgres.dept import Dept
from domino.databases.oracle import Oracle, RawToHex
 
class Page(BasePage):
    def __init__(self, application, request):
        super().__init__(application, request)
        self.postgres = None
        self.account_db = None
        self.database_id = self.attribute('database_id')

    def execute(self):
        table = Table(self, 'table').mt(1)
        sql = self.get('sql')
        if not sql:
            self.error('Пустой запрос')
            return
        ORACLE = None
        try:
            database = self.account_db.query(Database).get((self.account_id, self.database_id))
            ORACLE = Oracle.Pool().session(self.account_id, dept_code = database.database_id)
            cur = ORACLE.execute(sql)
            for column in cur.cursor.description:
                table.column().text(column[0])
            for r in cur.fetchmany(100):
                row = table.row()
                for value in r:
                    if isinstance(value, bytes):
                        value = RawToHex(value)
                    row.cell(style='white-space:nowrap').text(value)
        except Exception as ex:
            log.exception(__file__)
            self.error(f'{ex}')
        finally:
            if ORACLE:
                ORACLE.close()

    def __call__(self):
        database = self.account_db.query(Database).get((self.account_id, self.database_id))
        Title(self, f'{database.user_name}@{database.host}:{database.port}/{database.service_name}')
        sql = InputText(self, name='sql').style('font-size:1.5rem')
        toolbar = Toolbar(self, 'toolbar').mt(1)
        Button(toolbar.item(), 'Выполнить').onclick('.execute', forms=[sql])

        Table(self, 'table')
        


