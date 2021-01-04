from . import Page as BasePage
from . import Input, Title, Toolbar, Table, FlatTable
from . import log
from domino.account import Account

class Page(BasePage):
    def __init__(self, application, request):
        super().__init__(application, request)

    def change(self):
        account = Account(self.account_id)
        description = self.get('description')
        if description:
            account.description = description
            self.message(f'{description}')
            account.save()
    
    def __call__(self):
        Title(self, 'Настройка')

        account = Account(self.account_id)
        table = FlatTable(self, 'params')
        row = table.row()
        Input(row.cell(), label='наименование учетной записи', name='description', value=account.description)\
            .onkeypress(13, '.change', forms=[table])

        
