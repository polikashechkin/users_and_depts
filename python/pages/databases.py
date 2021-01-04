import os, json, sys
from . import Page as BasePage
from domino.pages import Button, IconButton, TextWithComments, DeleteIconButton, EditIconButton, Toolbar
from domino.core import log
from domino.tables.account_db.database import Database
from domino.tables.postgres.dept import Dept
import cx_Oracle
 
class Page(BasePage):
    def __init__(self, application, request):
        super().__init__(application, request)
        self.postgres = None
        self.account_db = None

    def delete(self):
        pass

    def check_database(self):
        #account_id = self.get('account_id')
        database_id = self.get('database_id')
        database = self.account_db.query(Database).get((self.account_id, database_id))
        try:
            conn = cx_Oracle.connect(user = database.scheme, password = database.scheme, dsn = database.dsn, encoding = "UTF-8", nencoding = "UTF-8") 
            conn.close()
            connection = True
        except BaseException as ex:
            self.error(f'{ex}')
            connection=False

        row = self.Row('databases', f'{database_id}')
        self.print_row(row, database, connection)

    def print_row(self, row, database, connection = None):
        #row.text(database.account_id)
        cell = row.cell()
        if database.database_id:
            comments = [database.database_id]
            dept = self.postgres.query(Dept).filter(Dept.guid == database.database_id).first()
            if dept:
                TextWithComments(cell, f'{dept.id}, {dept.name}', comments)
            else:
                cell.style('color:red')
                TextWithComments(cell, 'Неизвестное подразделение'.upper(), comments)
        else: 
            cell.text('Основная база данных'.upper())
        row.href(f'{database.dsn}', 'pages/oracle_monitor', {'account_id':database.account_id, 'database_id':database.database_id})
        row.href(f'{database.user_name}', 'pages/database_sql', {'database_id':database.database_id})
        #row.cell().text(f'{database.user_name}')
        #--------------------------------------
        cell = row.cell(align='right')
        if connection is None:
            Button(cell, 'Проверить').onclick('.check_database', {'account_id':database.account_id, 'database_id':database.database_id})
        elif connection :
            Button(cell, 'Доступна', style='color:white; background-color:green')
        else:
            Button(cell, 'Не доступна', style='color:white; background-color:red')
        #--------------------------------------
        cell = row.cell(width=2, align='right', style='white-space:nowrap')
        #IconButton(cell, 'edit', style='color:lightgray').onclick('pages/database', {'database_id':database.database_id})
        EditIconButton(cell).onclick('pages/database', {'database_id':database.database_id})
        if database.database_id:
            DeleteIconButton(cell).onclick('.delete', {'database_id':database.database_id})
        else:
            DeleteIconButton(cell).style('color:lightgray')
     
    def check_base_oracle_database(self):
        database  = self.account_db.query(Database).get((self.account_id, Database.BASE_DATABASE))
        if not database:
            database = Database(
                account_id = self.account_id,  database_id=Database.BASE_DATABASE,
                scheme = f'd{self.account_id}', host = 'localhost', port = 1521, service_name  = 'orcl'
                )
            self.account_db.add(database)
            self.account_db.commit()

    def __call__(self):
        self.title(f'Базы данных')

        self.check_base_oracle_database()
        
        toolbar = Toolbar(self, 'toolbar').mb(0.5)
        Button(toolbar.item(ml='auto'), 'Добавить базу данных').onclick('pages/database_add')

        databases = self.table('databases')
        databases.column().text('Описание')
        databases.column().text('Сервер')
        databases.column().text('БД')
        databases.column()

        for database in self.account_db.query(Database)\
                .filter(Database.account_id == self.account_id)\
                .order_by(Database.account_id, Database.database_id):
            row = databases.row(database.database_id)
            self.print_row(row, database)
