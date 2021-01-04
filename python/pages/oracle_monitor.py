import datetime, os, arrow, threading, cx_Oracle
#import tailer
from domino.core import log, DOMINO_ROOT
from . import Page as BasePage
from . import Table, Rows, Button, DeleteIconButton, Toolbar, Input
from domino.databases.oracle import Databases

class Page(BasePage):
    def __init__(self, application, request):
        super().__init__(application, request)
        self.database = Databases().get_database(self.account_id)
        self.hostname = self.application.hostname
    
    def connect_as_sysdba(self, password):
        return self.database.connect_sysdba('SYS', password)

    def clear(self):
        self.print_table()
    
    def delete(self):
        SID = int(self.get('sid'))
        SERIAL = self.get('serial')
        password = self.get('password')
        try:
            conn = self.connect_as_sysdba(password)
            cur = conn.cursor()
        except BaseException as ex:
            log.exception(__file__)
            self.error(f'{ex}')
            return
        #conn.close()
        sql = f"ALTER SYSTEM KILL SESSION '{SID},{SERIAL}' IMMEDIATE"
        params = []
        try:
            cur.execute(sql, params)
        except BaseException as ex:
            log.exception(__file__)
            self.error(f'{ex}')
            return
        finally:
            cur.close()
            conn.close()
        self.print_table()

    def print_table(self):
        #n = int(self.get('show_lines', 100))
        password = self.get('password')
        try:
            conn = self.connect_as_sysdba(password)
            cur = conn.cursor()
        except BaseException as ex:
            log.exception(__file__)
            self.error(f'{ex}')
            return
        #conn.close()
        sql = '''
            select 
                s.SID, s.SERIAL#, s.OSUSER, s.MACHINE, s.STATUS, s.USERNAME, 
                s.COMMAND, c.COMMAND_NAME, s.SQL_EXEC_START, 
                s.PREV_SQL_ID, s.SQL_EXEC_ID
                from v$session s, v$sqlcommand c
                WHERE c.command_type = s.command and s.MACHINE=:0 
            '''
            #and s.SQL_EXEC_ID = sql.KEY(+)
        params = [self.hostname]
        try:
            cur.execute(sql, params)
            rows = cur.fetchall()
        except BaseException as ex:
            log.exception(__file__)
            self.error(f'{ex}')
            return
        finally:
            cur.close()
            conn.close()
        
        count = 0
        table = Table(self, 'table').mt(1)
        table.column().text('ID')
        table.column().text('Статус')
        table.column().text('Схема')
        table.column().text('Компьютер')
        table.column().text('Команда')
        table.column()
        table.column()
        for SID, SERIAL, OUSER, MACHINE, STATUS, USERNAME, COMMAND, COMMAND_NAME, EXEC_START, PREV_SQL_ID, SQL_EXEC_ID in rows:
            count += 1
            row = table.row(SID)
            #row.cell(width=1).text(count)
            row.cell(width=1).text(f'{SID}:{SERIAL}')
            row.cell(width=10).text(STATUS)
            row.cell().text(USERNAME)
            row.cell().text(MACHINE)
            row.cell().text(COMMAND_NAME)
            row.cell().text(EXEC_START)
            DeleteIconButton(row.cell(align='right'))\
                .onclick('.delete', {'sid' : SID, 'serial':SERIAL, 'password':password})
        self.message(f'Всего сессий {count}')

    def print_toolbar(self):
        toolbar = Toolbar(self, 'toolbar')
        Input(toolbar.item(mr=1), label='Пароль SYS', name='password')
        Button(toolbar.item(), 'Показать сессии').onclick('.print_table', forms=[toolbar])
        #select = toolbar.item(ml=1).select(label= 'Строк', value='100', name='show_lines')
        #select.option('100', '100')
        #select.option('200', '200')
        #select.option('500', '500')
        #Button(toolbar.item(ml='auto'), 'Удалить сесии').onclick('.clear', forms=[toolbar])

    def __call__(self):
        self.title(f'{self.hostname}, {self.database.dsn}')
        #p = self.toolbar().item().text_block()
        #p.text(f'Имя компьютера ""')
        self.print_toolbar()
        Table(self, 'table')
