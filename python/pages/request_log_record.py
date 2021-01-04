import sys, os
from domino.core import log
from . import Page as BasePage
from . import Title, Toolbar, Input, InputText, Button, Table, Select, IconButton, Row, Text
from domino.tables.postgres.request_log import RequestLog
from domino.tables.postgres.dept import Dept

class Page(BasePage):
    def __init__(self, application, request):
        super().__init__(application, request)
        self.request_log_id = self.attribute('request_log_id')
        self.postgres = None

    def print_text(self, cell, text):
        if text.startswith('error:'):
            cell.style('color:red')
            cell.text(text.replace('error:',''))
        elif text.startswith('header:'):
            cell.style('font-weight: bold')
            cell.text(text.replace('header:',''))
        else:
            cell.text(text)

    def __call__(self):
        request_log = self.postgres.query(RequestLog).get(self.request_log_id)
        Title(self, f'{request_log.path}')
        Text(self, 'url').text(request_log.url)
        info = request_log.info
        if info:
            protocol = info.get('protocol')
            if protocol:
                table = Table(self, 'protocol').mt(1)
                for r in protocol:
                    row = table.row()
                    if isinstance(r, (list, tuple)):
                        self.print_text(row.cell(), r[0])
                        time_ms = f'{round(r[1] * 1000, 1):,}'
                        row.cell(align='right').text(time_ms)
                    else:
                        self.print_text(row.cell(style='color:gray'), r)
                        row.cell()
