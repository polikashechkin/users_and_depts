from domino.core import log
from . import Page as BasePage
from . import Title, Toolbar, Input, InputText, Button, Table, Select, IconButton
from domino.tables.postgres.server import Server

class Page(BasePage):
    def __init__(self, application, request):
        super().__init__(application, request)

    def print_row(self, row, server):
        row.cell().text(server.id)
        row.cell().text(server.name)

    def print_table(self):
        table = Table(self, 'table').mt(1)
        for server in self.postgres.query(Server).order_by(Server.name):
            row = table.row(server.id) 
            self.print_row(row, server)

    def __call__(self):
        Title(self, 'Удаленные компьютеры')
        self.print_table()

