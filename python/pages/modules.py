import os, json, sys
from . import Page as BasePage
from . import Button, IconButton, TextWithComments, Title, Table, Text
from domino.core import log, DOMINO_ROOT
from domino.tables.postgres.user import User
from domino.tables.postgres.grant import Grant
from domino.account import Account
from components.module import Module

УПРАВЛЯЮЩИЙ = 'Управляющий'
СИСТЕМНЫЙ_АДМИНИСТРАТОР = 'Sysadmin'
 
class Page(BasePage):
    def __init__(self, application, request):
        super().__init__(application, request)
        self.postgres = None
    
    def _granted_users(self, module, grant_id):
        users = []
        query = self.postgres.query(User.name).join(Grant, Grant.user_id == User.id)\
                .filter(Grant.module_id == module.grant_module_id, Grant.grant_id == grant_id)\
                .filter(Grant.NoObject)
        for user_name, in query:
            users.append(user_name)
        return ', '.join(users)

    def print_row(self, row, module):
        cell = row.cell()
        #grant_mode = 'Общедоступный' if module.is_public else ''
        TextWithComments(cell, module.name, [module.id, f'Версия "{module.version}'])
        #--------------------------------
        cell = row.cell()
        users = self._granted_users(module, Grant.MANAGER)
        if module.external_grants:
            cell.text(users)
        else:
            if users:
                cell.href(users,'domino/pages/granted_users', {'module_id':module.id, 'grant_id': Grant.MANAGER, 'grant_name':УПРАВЛЯЮЩИЙ})
            else:
                cell.href('НЕТ НАЗНАЧЕНИЙ','domino/pages/granted_users', {'module_id':module.id, 'grant_id': Grant.MANAGER, 'grant_name':УПРАВЛЯЮЩИЙ}, style='color:lightgray')
                #Button(cell, 'Назначить').onclick('pages/sysadmins', {'module_id':module.id, 'grant_id': Grant.MANAGER})
        #--------------------------------
        cell = row.cell()
        users = self._granted_users(module, Grant.SYSADMIN)
        if module.external_grants:
            cell.text(users)
        else:
            if users:
                cell.href(users,'domino/pages/granted_users', {'module_id':module.id, 'grant_id': Grant.SYSADMIN, 'grant_name':СИСТЕМНЫЙ_АДМИНИСТРАТОР})
            else:
                cell.href('НЕТ НАЗНАЧЕНИЙ','domino/pages/granted_users', {'module_id':module.id, 'grant_id': Grant.SYSADMIN, 'grant_name':СИСТЕМНЫЙ_АДМИНИСТРАТОР}, style='color:lightgray')
                #Button(cell, 'Назначить').onclick('pages/sysadmins', {'module_id':module.id, 'grant_id': Grant.SYSADMIN})
        #--------------------------------
        row.cell().link(f'{module.version}').onclick('pages/version_history', {'module_id':module.id, 'module_name':module.name})

    def get_account_products(self):
        r = set()
        for product in self.account.info.get('products'):
            r.add(product['id'])
        return r

    def print_table(self):
        self.account = Account(self.account_id)
        table = Table(self, 'table')
        table.column().text('Модуль')
        table.column().text(УПРАВЛЯЮЩИЙ)
        table.column().text(СИСТЕМНЫЙ_АДМИНИСТРАТОР)
        table.column().text('Версия')
        products = self.get_account_products()
        products_folder = os.path.join(DOMINO_ROOT, 'products')
        for module_id in os.listdir(products_folder):
            if module_id in products:
                module = Module.get(module_id)
                if module and module.is_login:
                    row = table.row(module.id)
                    self.print_row(row, module)

    def __call__(self):
        Title(self, f'Модули')
        self.print_table()
           
