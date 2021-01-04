from domino.core import log
from . import Title, Text
from domino.account import Account
from domino.pages.start_page import Page as BasePage

class Page(BasePage):
    def __init__(self, application, request):
        super().__init__(application, request)

    def create_menu(self, menu):
        group = menu.group('Администрирование и настройка')
        group.item('Журналы', 'pages/request_log')
        group.item('Удаленные компьютеры', 'pages/servers')
        group.item('Базы данных', 'pages/databases')
        group.item('Процедуры', 'domino/pages/procs')
        group.item('Настройка', 'pages/settings')

    def __call__(self):
        account = Account(self.account_id)
        Title(self, f'{account.id}, {account.info.name}')
        self.print_menu()

