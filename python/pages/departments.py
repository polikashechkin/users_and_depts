from domino.core import log
from . import Page as BasePage
from . import Title, Toolbar, Input, InputText, Button, Table, Select, IconButton, TextWithComments, EditIconButton
from domino.tables.postgres.dept_param import DeptParam
from domino.tables.postgres.dept import Dept
from domino.tables.postgres.organization import Organization
from domino.tables.postgres.dictionary import Dictionary
from sqlalchemy import func as F, text as T

class Page(BasePage):
    def __init__(self, application, request):
        super().__init__(application, request)
        self.postgres = None

    #def query_columns(self):
    #    return self.postgres.query(Dictionary).filter(Dictionary.DeptColumns).all()

    def print_row(self, row, dept, organization):
        TextWithComments(row.cell(), dept.id, [dept.UID] if dept.UID else None)
        #----------------------------------
        props = []
        if dept.description is not None:
            for prop_name, prop_value in dept.description.items():
                props.append(f'{prop_name} "{prop_value}"')
        if organization:
            props.append(f'Организация "{organization.name}"')
        if dept.address:
            props.append(f'Адрес "{dept.address}"')
        if dept.guid: 
            props.append(f'Guid "{dept.guid}"')
        TextWithComments(row.cell(), dept.name, props)
        #row.cell().html(f'''{dept.name}<p style="font-size:small;color:gray; line-height: 1em">{', '.join(props)}</p>''')
        #----------------------------------
        #row.cell().text(dept.address)
        #----------------------------------
        EditIconButton(row.cell(width=2))\
            .onclick('pages/department', {'dept_id': dept.id})

    def print_table(self):
        log.debug(f'print_table')
        table = Table(self, 'table').mt(1)
        table.column().text('Код')
        table.column().text('Наименование')
        #table.column().text('Адрес')
        query = self.postgres.query(Dept, Organization).outerjoin(Organization, Organization.id == Dept.organization_id)
        name = self.get('name')
        if name:
            query = query.filter(Dept.name.ilike(f'%{name}%'))

        for param in DeptParam.all(self.postgres):
            value = self.get(param.id)
            if value:
                query = query.filter(T(f"{param.id} = '{value}'"))
 
        for dept, organization in query.order_by(Dept.name):
            row = table.row(dept.id) 
            self.print_row(row, dept, organization)

    def __call__(self):
        Title(self, 'Подразделения')
        toolbar = Toolbar(self, 'toolbar')
        Input(toolbar.item(mr=0.5), name='name', label='Наименование')\
            .onkeypress(13, '.print_table', forms=[toolbar])

        for param in DeptParam.all(self.postgres):
            select = Select(toolbar.item(ml=0.5) , name=param.id, label=param.name)\
                     .onchange('.print_table', forms=[toolbar])
            select.option('', '')
            select.options(param.options(self.postgres))

        self.print_table()

