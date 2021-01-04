from domino.core import log
from . import Page as BasePage
from . import Title, Toolbar, Input, InputText, Button, Table, TextWithComments, Rows
from . import IconButton, EditIconButton, DeleteIconButton, CheckIconButton

from domino.tables.postgres.user import User
from domino.tables.postgres.grant import Grant

class Page(BasePage):
    def __init__(self, application, request):
        super().__init__(application, request)
        self.postgres = None

    def delete(self):
        user_id = self.get('user_id')
        self.postgres.query(User).filter(User.id == user_id).delete()
        Rows(self, 'table').row(user_id)
    
    def enable_disable(self):
        user_id = self.get('user_id')
        user = self.postgres.query(User).get(user_id)
        if user.disabled:
            user.disabled = False
            self.message(f'Пользователь доступен')
        else:
            user.disabled = True
            self.postgres.query(Grant).filter(Grant.user_id == user_id).delete()
            self.message(f'Пользователь заблокирован. Все права аннулированы.')
        row = Rows(self, 'table').row(user_id)
        self.print_row(row, user)

    def print_row(self, row, user):
        CheckIconButton(row.cell(width=2), not user.disabled)\
            .onclick('.enable_disable', {'user_id':user.id})
        comments = []
        if user.full_name:
            comments.append(user.full_name)
        if user.UID:
            comments.append(user.UID)
        TextWithComments(row.cell(), user.name, comments)
        cell = row.cell(align='right', width=6)
        if user.name != 'FIRST_USER':
            EditIconButton(cell).onclick('pages/user', {'user_id':user.id})
            DeleteIconButton(cell).onclick('.delete', {'user_id':user.id})

    def print_table(self):
        table = Table(self, 'table').mt(1)
        query = self.postgres.query(User).order_by(User.name)
        name = self.get('name')
        if name:
            query = query.filter(User.name.ilike(f'%{name}%'))
        for user in query.limit(200):
            self.print_row(table.row(user.id), user)

    def __call__(self):
        Title(self, 'Пользователи')
        toolbar = Toolbar(self, 'toolbar')
        Input(toolbar.item(), label='Наименование', name='name')\
            .onkeypress(13, '.print_table', forms=[toolbar])
        Button(toolbar.item(ml='auto'), 'Создать').onclick('pages/create_user')
        self.print_table()

