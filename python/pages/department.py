from domino.core import log
from . import Page as BasePage
from . import Title, Toolbar, Input, InputText, Button, Table, Select
from domino.tables.postgres.dept import Dept
from domino.tables.postgres.organization import Organization
 
class Page(BasePage):
    def __init__(self, application, request):
        super().__init__(application, request)
        self.dept_id = self.attribute('dept_id')

    def change(self):
        dept = self.postgres.query(Dept).get(self.dept_id)
        dept.address = self.get('address')
        dept.organization_id = self.get('organization_id')

    def __call__(self):
        dept = self.postgres.query(Dept).get(self.dept_id)
        Title(self, f'{dept.id} {dept.name}')
        params = Table(self, 'params')
        row = params.row()
        row.cell(width=20).text('Адрес')
        cell = row.cell()
        #cell.style('border:1px solid gray')
        Input(cell, name='address', value=dept.address)

        row = params.row()
        row.cell().text('Организация')
        select = Select(row.cell(), name='organization_id', value=dept.organization_id)
        for o in self.postgres.query(Organization):
            select.option(o.id, o.name)

        toolbar = Toolbar(self, 'toolbar').mt(1)
        Button(toolbar, 'Изменить').onclick('.change', forms=[params])

