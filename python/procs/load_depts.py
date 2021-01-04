import os, sys, datetime, time, json, sqlite3
from sqlalchemy import delete, insert, select, update, text as T, func as F

#from lxml import etree
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.append(path)

from domino.core import log, DOMINO_ROOT
from domino.jobs import Proc
from domino.databases.postgres import Postgres
from domino.databases.oracle import Oracle
from pages import Page as BasePage
from pages import Title, Text, Table

from settings import MODULE_ID

from domino.tables.postgres.user import User
from domino.tables.postgres.dept import Dept, DeptTable
from domino.tables.postgres.dictionary import Dictionary, DictionaryTable
from domino.tables.postgres.dept_param import DeptParam

DESCRIPTION = 'Загрузка справочника подразделений'
PROC_ID = 'procs/load_depts.py'

def on_activate(account_id, msg_log): 
    Proc.create(account_id, MODULE_ID, PROC_ID, description=DESCRIPTION, url='procs/load_depts')

def get_agent_name(oracle, e_code):
    #log.debug(f'{db_cursor}, {e_code}')
    sql = 'select name from db1_agent where id = :id'
    r = oracle.execute(T(sql), {'id' : e_code}).fetchone()
    return r[0] if r is not None else None

class D_Column:
    def __init__(self, column, name, get_db_name):
        self.column = column
        self.id = column.name
        self.name = name
        self.get_db_name = get_db_name
        self.dictionary_def = None
        self.e_dictionary = {}

    def create(self, postgres):
        self.dept_param = postgres.query(DeptParam).get(self.id)
        if self.dept_param:
            self.dept_param.name = self.name
        else:
            self.dept_param = DeptParam(id=self.id, name=self.name)
            postgres.add(self.dept_param)
        postgres.commit()

        self.dictionary_def = postgres.query(Dictionary)\
            .filter(Dictionary.CLASS == 'dept', Dictionary.TYPE == 'column', Dictionary.code == self.id)\
            .one_or_none()
        if self.dictionary_def:
            self.dictionary_def.name = self.name
        else:
            self.dictionary_def = Dictionary(CLASS = 'dept', TYPE = 'column', state = 0, code = self.id, name=self.name)
            postgres.add(self.dictionary_def)
        postgres.commit()

        for dictionary in postgres.query(Dictionary)\
                .filter(Dictionary.CLASS == 'dept', Dictionary.TYPE == self.id):
            self.e_dictionary[dictionary.e_code] = dictionary

    def get_dictionary(self, oracle, postgres, e_code):
        dictionary = self.e_dictionary.get(e_code)
        if dictionary is not None:
            return dictionary
        else:
            name = self.get_db_name(oracle, e_code)
            if name is None:
                name = f''
            dictionary = Dictionary(CLASS = 'dept', TYPE = self.id, state=0, e_code = e_code, name = name)
            postgres.add(dictionary)
            postgres.commit()
            self.e_dictionary[e_code] = dictionary
            return dictionary
 
    def check_state(self, job):
        count = job.postgres.query(F.count()).filter(Dictionary.CLASS == 'dept', Dictionary.TYPE == self.id).limit(1).scalar()
        disabled = (count == 0)
        job.postgres.query(DeptParam).filter(DeptParam.id == self.id).update({'disabled':disabled})
        job.log(f'{self.id} : {self.name} : {len(self.e_dictionary)} : {count} => {not disabled}')
        job.postgres.commit()

class D_Columns:

    all_columns = [
        D_Column(Dept.f28835888, 'Ценовой формат', get_agent_name)
    ]

    def __init__(self, oracle):
        #--------------------------------------------
        names = set()
        sql = "select column_name from user_tab_columns where table_name = 'DB1_AGENT'"
        for column_name, in oracle.execute(T(sql)):
                names.add(column_name.lower())
        #--------------------------------------------
        self.columns = []
        for column in D_Columns.all_columns:
            if column.id in names:
                self.columns.append(column) 
        #--------------------------------------------
        if len(self.columns):
            fields = []
            query = []
            for column in self.columns:
                fields.append(f'rawtohex({column.id})')
                query.append('%s')
            self.DB_SELECT = f'select id, code, name, {", ".join(fields)} from db1_agent where class=2 and type=40566786 and name is not null'
        else:
            self.DB_SELECT = f'select id, code, name from db1_agent where class=2 and type=40566786 and name is not null'

    def create(self, postgres):
        for column in self.columns:
            column.create(postgres)

class Page(BasePage):
    def __init__(self, application, request):
        super().__init__(application, request)
        self.proc = Proc.get(self.account_id, MODULE_ID, PROC_ID)

    def __call__(self):
        Title(self, f'{self.proc.ID}, {DESCRIPTION}')
        Text(self).text('''
        Загрузка и обновление справочника подразделений. 
        При загрузке подразделений загружаются также некоторые параметры подраззделений.
        Загружаются только те параметры, которые определены в базе данных.
        ''')
        Text(self).mt(1).text('Таблица возможных параметров подразделений')
        table = Table(self, 'dept_params')

        for column in D_Columns.all_columns:
            row = table.row()
            row.cell().text(column.id)
            row.cell().text(column.name)

class Job(Proc.Job): 
    def __init__(self, ID):
        super().__init__(ID)

    def __call__(self):
        self.proc = Proc.get(self.account_id, MODULE_ID, PROC_ID)
        self.log('НАЧАЛО')

        stop_reason = ''
        self.postgres = Postgres.Pool().session(self.account_id)
        self.oracle = Oracle.Pool().session(self.account_id)
        try:
            self.dowork()
            self.postgres.commit()
        except BaseException as ex:
            log.exception(__file__)
            self.postgres.rollback()
            stop_reason = f'{ex}'
        finally:
            self.postgres.close()
            self.oracle.close()

        self.log(f'ОКОНЧАНИЕ {stop_reason}')
    
    def dowork(self):
        self.load_depts()
        #self.load_registered_depts()

    def load_depts(self):
        self.log(f'ЗАГРУЗКА ПОДРАЗДЕЛЕНИЙ')
        d_columns = D_Columns(self.oracle)
        d_columns.create(self.postgres)
        self.log(d_columns.DB_SELECT)
        # -----------------------------------------------
        count = 0
        updated = 0
        created = 0
        errors = 0 
        #select_cursor = self.db_connection.cursor()
        select_cursor = self.oracle.execute(T(d_columns.DB_SELECT))
        for db_row in select_cursor:
            UID = db_row[0] 
            ID = db_row[1]
            NAME = db_row[2]
            VALUES = db_row[3:]
            #self.log(f'id={ID}, name={NAME}, values={VALUES}')
            #if count > 5:
            #    break
            count += 1
            if count % 1000 == 0:
                self.log(f'Обработано {count}, обновлено {updated}, создано {created}, ошибок {errors}')
                self.postgres.commit()
            try:
                values = {}
                description = {}
                for i in range(len(VALUES)):
                    column = d_columns.columns[i]
                    dictionary = column.get_dictionary(self.oracle, self.postgres, VALUES[i])
                    description[column.name] = dictionary.name
                    values[column.id] = dictionary.id
                #self.log(f'values={values}, description={description}')
                # ---------------------------------------------
                dept = self.postgres.query(Dept).get(ID)
                if dept:
                    values[DeptTable.c.uid] = UID
                    values[DeptTable.c.description] = description
                    values[DeptTable.c.name] = NAME
                    self.postgres.execute(update(DeptTable, values = values).where(DeptTable.c.id == ID))
                    updated += 1
                else:                
                    values[DeptTable.c.uid] = UID
                    values[DeptTable.c.id] = ID
                    values[DeptTable.c.name] = NAME
                    values[DeptTable.c.description] = description
                    Dept.insert(self.postgres, values)
                    created += 1
            except BaseException as ex:
                errors += 1
                self.log(f'{count} : {ID}, {NAME} : {ex}')
                log.exception(__file__)

        self.postgres.commit()
        self.log(f'Всего обработано {count}, обновлено {updated}, создано {created}, ошибок {errors}')
        self.log('ПРОВЕРКА И РЕОРГАНИЗАЦИЯ СПРАВОЧНИКОВ')
        for column in d_columns.columns:
            column.check_state(self)
        self.log('ЗАГРУЗКА ПОДРАЗДЕЛЕНИЙ ЗАВЕРШЕНА')

        self.log(f'ЗАГРУЗКА РЕГИСТРАЦИОННЫХ ДАННЫХ')
        count = 0
        updated = 0
        errors = 0
        with sqlite3.connect(os.path.join(DOMINO_ROOT, 'data', 'account.db')) as conn:
            cur = conn.cursor()
            sql = 'select guid, code from depts where account_id=? and type=? and code != "."'
            cur.execute(sql, [self.account_id, 'LOCATION'])
            for guid, code in cur:
                if not guid or not code:
                    continue
                count += 1
                dept = self.postgres.query(Dept).get(code)
                self.log(f'dept {code} => {guid}')
                if dept:
                    dept.guid = guid
                    updated += 1
                else:
                    errors += 1
                    self.log(f'Не найдено подразделение "{code}"')
        self.log(f'Обработано {count}, обновлено {updated}, ошибок {errors}')

if __name__ == "__main__":
    try:
        with Job(sys.argv[1]) as job:
            job()
    except:
        log.exception(__file__)
    