from domino.core import log
from . import Page as BasePage
from . import Title, Toolbar, Input, InputText, Button, Table, Select
from domino.tables.postgres.user import User
 
class Page(BasePage):
    def __init__(self, application, request):
        super().__init__(application, request)
        self.postgres = None

    def create(self):
        name = self.get('name')
        if not name:
            self.error('Имя должно быть задано')
            return
        full_name = self.get('full_name')
        user = self.postgres.query(User).get(name)
        if user:
            self.error('Пользователь с таким имененм уже есть')
            return
        user = User(id=name, name=name, full_name = full_name)
        self.postgres.add(user)
        self.message(f'{name}, {full_name}')
        
    def __call__(self):
        Title(self, f'Новый пользователь')
        params = Toolbar(self, 'params')
        Input(params.item(mr=0.5), name='name', label='Имя')
        Input(params.item(mr=0.5), name='full_name', label='Полное имя').width(30)
        toolbar = Toolbar(self, 'toolbar').mt(1)
        Button(toolbar, 'Создать').onclick('.create', forms=[params])

