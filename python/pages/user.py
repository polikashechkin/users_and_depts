from domino.core import log
from . import Page as BasePage
from . import Title, Toolbar, Input, InputText, Button, Table, Select
from domino.tables.postgres.user import User
 
class Page(BasePage):
    def __init__(self, application, request):
        super().__init__(application, request)
        self.postgres = None
        self.user_id = self.attribute('user_id')

    def change(self):
        full_name = self.get('full_name')
        user = self.postgres.query(User).get(self.user_id)
        user.full_name = full_name
        self.message(f'{full_name}')
        
    def __call__(self):
        user = self.postgres.query(User).get(self.user_id)
        Title(self, f'{user.name}')
        params = Toolbar(self, 'params')
        Input(params.item(mr=0.5), name='full_name', label='Полное имя', value=user.full_name).width(30)
        toolbar = Toolbar(self, 'toolbar').mt(1)
        Button(toolbar, 'Изменить').onclick('.change', forms=[params])

