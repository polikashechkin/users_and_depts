import sys, os, html
from domino.core import log
from . import Page as BasePage
from . import Title, Toolbar, Input, InputText, Button, Table, Select, IconButton, Rows, DeleteIconButton
from . import BookmarkIconButton
from domino.tables.postgres.request_log import RequestLog
from domino.tables.postgres.dept import Dept
from sqlalchemy import or_, and_

class Page(BasePage):
    def __init__(self, application, request):
        super().__init__(application, request)
        self.postgres = None

    def on_delete(self):
        id = self.get('id')
        self.postgres.query(RequestLog).filter(RequestLog.id == id).delete()
        Rows(self, 'table').row(id)

    def clean(self):
        self.postgres.query(RequestLog).filter(or_(RequestLog.fixed == False, RequestLog.fixed == None)).delete()
        self.print_table()

    def bookmark(self):
        request_log_id = self.get('request_log_id')
        request_log = self.postgres.query(RequestLog).get(request_log_id)
        dept = self.postgres.query(Dept).get(request_log.dept_code)
        request_log.fixed = not request_log.fixed
        row = Rows(self, 'table').row(request_log_id)
        self.print_row(row, request_log, dept)

    def print_row(self, row, request_log, dept):
        #-----------------------------------------
        cell = row.cell(width=2)
        button = BookmarkIconButton(cell, request_log.fixed)
        button.onclick('.bookmark', {'request_log_id':request_log.id})
        #-----------------------------------------
        cell = row.cell(width=2)
        if request_log.is_test:
            cell.glif('circle', css='-text-danger', style='font-size:small; color:orange').tooltip('Тестовый вызов')
        #-----------------------------------------
        if request_log.status_code:
            cell.glif('star', css='-text-danger', style='font-size:small; color:red')\
                .tooltip(html.escape(f'Код возврата : {request_log.status_code} : {request_log.response_text}'))
        #-----------------------------------------
        row.cell(width=0).text(request_log.id).tooltip(f'Номер "{request_log.id}", модуль "{request_log.module_id}"')
        #row.cell(style='white-space:nowrap').text(request_log.module_id)
        row.cell(width=0, style='white-space:nowrap').text(request_log.ctime.strftime('%Y-%m-%d %H:%M:%S')).tooltip(request_log.ctime)
        #-----------------------------------------
        text = row.cell().text_block()
        text.href(request_log.path, 'pages/request_log_record', { 'request_log_id':request_log.id})
        if request_log.xml_file:
            #IconButton(text, 'help_outline', style='color:lightgray')\
            #.onclick('show_file.request_log_xml_file', {'account_id':self.account_id,'request_log_id':request_log.id}, target='NEW_WINDOW')
            text.href('xml_file', 'show_file.request_log_xml_file', {'account_id':self.account_id,'request_log_id':request_log.id}, new_window = True)
        #-----------------------------------------
        row.cell().text(request_log.comment)
        #-----------------------------------------
        cell = row.cell()
        if dept:
            cell.text(dept.name).tooltip(request_log.dept_code)
        else:
            cell.text(request_log.dept_code)
        #-----------------------------------------
        response_type = request_log.response_type if request_log.response_type else 'text'
        size = len(request_log.response_text) if request_log.response_text else '0'
        #status_code = request_log.status_code if request_log.status_code else '200'
        text = row.cell().text_block()
        if request_log.response_text:
            #text.text(f'{response_type} ({size})')
            #IconButton(text, 'help_outline', style='color:lightgray')\
            #.onclick('show_file.request_log_response_text', {'account_id':self.account_id,'request_log_id':request_log.id}, target='NEW_WINDOW')
            text.href(f'{response_type} ({size})', 'show_file.request_log_response_text', {'account_id':self.account_id,'request_log_id':request_log.id}, new_window=True)
            #IconButton(text, 'help_outline', style='color:lightgray')\
            #.onclick('show_file.request_log_response_text', {'account_id':self.account_id,'request_log_id':request_log.id}, target='NEW_WINDOW')

        #------------------------------------------
        cell = row.cell(width=2, align='right')
        if request_log.duration:
            cell.text(f'{round(request_log.duration * 1000, 1)}')
        #------------------------------------------
        cell = row.cell(width=2)
        DeleteIconButton(cell).onclick('.on_delete', {'id':request_log.id})

    def print_table(self):
        table = Table(self, 'table').mt(1)
        table.column()
        table.column()
        table.column().text('#')
        table.column().text('Дата+Время')
        table.column().text('Запрос')
        table.column().text('Примечание')
        table.column().text('Подразделение')
        table.column().text('Ответ')
        table.column(align='right').text('мс')
        table.column()
        #---------------------------------
        query = self.postgres.query(RequestLog, Dept)\
            .outerjoin(Dept, Dept.id == RequestLog.dept_code)
        #---------------------------------
        module_id = self.get('module_id')
        if module_id:
            query = query.filter(RequestLog.module_id == module_id)
        #---------------------------------
        comment = self.get('comment')
        if comment:
            query = query.filter(RequestLog.comment.ilike(f'%{comment}%'))
        #---------------------------------
        dept_code = self.get('dept_code')
        if dept_code:
            query = query.filter(RequestLog.dept_code == dept_code)
        #---------------------------------
        for request_log, dept in query.order_by(RequestLog.ctime.desc()).limit(200):
            row = table.row(request_log.id) 
            self.print_row(row, request_log, dept)

    def __call__(self):
        Title(self, f'Журналы вызовов')
        toolbar = Toolbar(self, 'toolbar')
        #-------------------------------------
        select = Select(toolbar.item(mr=0.5), name='module_id', label='Журнал')\
            .onchange('.print_table', forms=[toolbar])
        select.option('','')
        select.option('m-assist', 'Мобильный помошник')
        select.option('discount', 'Дисконтный сервер')
        select.option('w2pos', 'Возврат чеков')
        select.option('login', 'Вход в систему')
        select.option('d_cards', 'Дисконтные карты')
        #-------------------------------------
        Input(toolbar.item(mr=0.5), name='comment', label='Примечание')\
            .onkeypress(13, '.print_table', forms=[toolbar])
        #-------------------------------------
        select = Select(toolbar.item(mr=0.5), name='dept_code', label='Подразделение')\
            .onchange('.print_table', forms=[toolbar])
        select.option('','')
        for dept in self.postgres.query(Dept).order_by(Dept.name):
            select.option(dept.id, dept.name)
        #-------------------------------------
        Button(toolbar.item(ml='auto'), 'Очистить').onclick('.clean')
        self.print_table()

