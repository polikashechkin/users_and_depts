from domino.core import log
from . import Page as BasePage
from . import Title, Toolbar, Input, InputText, Button, Table, Select, IconButton
from domino.tables.postgres.organization import Organization
from sqlalchemy import func as F, or_

class Page(BasePage):
    def __init__(self, application, request):
        super().__init__(application, request)
        self.postgres = None

    def create_organization(self):
        organization = Organization()
        #organization.inn = self.get('inn')
        organization.name = self.get('name')

        #if not organization.inn:
        #    self.error('Инн должен быть задан')
        #    return

        #if not organization.name:
        #    self.error('Имя должно быть задано')
        #   return
        
        #if self.postgres.query(F.count).select_from(Organization)\
        #    .filter(Organization.name == organization.name)\
        #   .scalar():
        #   self.error('Такая организация уже существует')
        #    return
        
        self.postgres.add(organization)
        self.message(f'{organization.name}')

    def __call__(self):
        Title(self, 'Добавить организацию')
        toolbar = Toolbar(self, 'toolbar')
        #Input(toolbar.item(), name='inn', label='Инн')
        Input(toolbar.item(), name='name', label='Наименование').width(50)
        actions = Toolbar(self, 'actions').mt(1)
        Button(actions.item(), 'Создать').onclick('.create_organization', forms=[toolbar])

