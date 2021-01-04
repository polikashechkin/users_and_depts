from domino.core import log
from . import Page as BasePage
from . import Title, Toolbar, Input, InputText, Button, Table, Select, IconButton
from domino.tables.postgres.organization import Organization

class Page(BasePage):
    def __init__(self, application, request):
        super().__init__(application, request)
        self.organization_id = self.attribute('organization_id')
 
    def change_params(self):
        o = self.postgres.query(Organization).get(self.organization_id)
        name = self.get('name')
        o.name = name
        Title(self, o.name)

    def __call__(self):
        o = self.postgres.query(Organization).get(self.organization_id)
        Title(self, o.name)
        table = Table(self, 'table')
        Input(table.row().cell(), name = 'name', value=o.name, label='Наименование')
        toolbar = Toolbar(self, 'toolbar')
        Button(toolbar.item(), 'Сохранить').onclick('.change_params', forms=[table])
