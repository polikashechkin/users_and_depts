from domino.core import log
from . import Page as BasePage
from . import Title, Toolbar, Input, InputText, Button, Table, Select, IconButton, EditIconButton
from domino.tables.postgres.organization import Organization

class Page(BasePage):
    def __init__(self, application, request):
        super().__init__(application, request)
        

    def print_row(self, row, organization):
        #row.cell().text(organization.id)
        #row.cell().text(organization.inn)
        row.cell().text(organization.name)
        cell = row.cell(width=2)
        EditIconButton(cell).onclick('pages/organization', {'organization_id':organization.id})

    def print_table(self):
        table = Table(self, 'table').mt(1)
        #table.column().text('Инн')
        #table.column().text('Наименование')

        for orgatization in self.postgres.query(Organization).order_by(Organization.name):
            row = table.row(orgatization.id)
            self.print_row(row, orgatization)

    def __call__(self):
        Title(self, 'Организации')
        toolbar = Toolbar(self, 'toolbar')
        Button(toolbar.item(ml='auto'), 'Создать').onclick('pages/organization_add')
        self.print_table()
