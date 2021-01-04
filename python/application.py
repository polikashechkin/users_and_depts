#< import 
import sys, os, time 
from flask import Flask, request
from domino.core import log
from domino.application import Application
from domino.databases.postgres import Postgres
#from domino.databases.account_db import AccountDb
from domino.account_db import AccountDb
                                 
ACCOUNT_DB = AccountDb.Pool()
POSTGRES = Postgres.Pool()
                           
app = Flask(__name__)
application = Application(os.path.abspath(__file__), framework='MDL')
       
#-------------------------------------------    

import domino.pages.granted_users
@app.route('/domino/pages/granted_users', methods=['POST', 'GET'])
@app.route('/domino/pages/granted_users.<fn>', methods=['POST', 'GET'])
def _domino_pages_granted_users(fn = None):
    return application.response(request, domino.pages.granted_users.Page, fn, [POSTGRES])

import domino.pages.module_history
@app.route('/domino/pages/module_history', methods=['POST', 'GET'])
@app.route('/domino/pages/module_history.<fn>', methods=['POST', 'GET'])
def _domino_pages_module_history(fn = None):
    return application.response(request, domino.pages.module_history.Page, fn)

import domino.pages.procs
@app.route('/domino/pages/procs', methods=['POST', 'GET'])
@app.route('/domino/pages/procs.<fn>', methods=['POST', 'GET'])
def _domino_pages_procs(fn = None):
    return application.response(request, domino.pages.procs.Page, fn)
  
import domino.pages.proc_shedule
@app.route('/domino/pages/proc_shedule', methods=['POST', 'GET'])
@app.route('/domino/pages/proc_shedule.<fn>', methods=['POST', 'GET'])
def _domino_pages_proc_shedule(fn = None):
    return application.response(request, domino.pages.proc_shedule.Page, fn)
  
import domino.pages.jobs
@app.route('/domino/pages/jobs', methods=['POST', 'GET'])
@app.route('/domino/pages/jobs.<fn>', methods=['POST', 'GET'])
def _domino_pages_jobs(fn = None):
    return application.response(request, domino.pages.jobs.Page, fn)

import domino.pages.job
@app.route('/domino/pages/job', methods=['POST', 'GET'])
@app.route('/domino/pages/job.<fn>', methods=['POST', 'GET'])
def _domino_pages_job(fn = None):
    return application.response(request, domino.pages.job.Page, fn)

import domino.responses.job
@app.route('/domino/job', methods=['POST', 'GET'])
@app.route('/domino/job.<fn>', methods=['POST', 'GET'])
def _domino_responses_job(fn=None):
    return application.response(request, domino.responses.job.Response, fn)
#-------------------------------------------    

import pages.start_page
@app.route('/pages/start_page', methods=['POST', 'GET'])
def _pages_start_page():
    return application.response(request, pages.start_page.Page, None)
@app.route('/pages/start_page.<fn>', methods=['POST', 'GET'])
def _pages_start_page_fn(fn):
    return application.response(request, pages.start_page.Page, fn)

import pages.version_history
@app.route('/pages/version_history', methods=['POST', 'GET'])
@app.route('/pages/version_history.<fn>', methods=['POST', 'GET'])
def _pages_version_history(fn = None):
    return application.response(request, pages.version_history.Page, fn)
        
import pages.users
@app.route('/pages/users', methods=['POST', 'GET'], defaults={'fn':None})
@app.route('/pages/users.<fn>', methods=['POST', 'GET'])
def _pages_users(fn):
    return application.response(request, pages.users.Page, fn, [POSTGRES])

import pages.user
@app.route('/pages/user', methods=['POST', 'GET'], defaults={'fn':None})
@app.route('/pages/user.<fn>', methods=['POST', 'GET'])
def _pages_user(fn):
    return application.response(request, pages.user.Page, fn, [POSTGRES])
 
import pages.create_user
@app.route('/pages/create_user', methods=['POST', 'GET'], defaults={'fn':None})
@app.route('/pages/create_user.<fn>', methods=['POST', 'GET'])
def _pages_create_user(fn):
    return application.response(request, pages.create_user.Page, fn, [POSTGRES])
 
import pages.modules
@app.route('/pages/modules', methods=['POST', 'GET'], defaults={'fn':None})
@app.route('/pages/modules.<fn>', methods=['POST', 'GET'])
def _pages_modules(fn):
    return application.response(request, pages.modules.Page, fn, [POSTGRES])
   
import pages.databases
@app.route('/pages/databases', methods=['POST', 'GET'])
def _pages_databases():
    return application.response(request, pages.databases.Page, None, [POSTGRES, ACCOUNT_DB])
@app.route('/pages/databases.<fn>', methods=['POST', 'GET'])
def _pages_databases_fn(fn):
    return application.response(request, pages.databases.Page, fn, [POSTGRES, ACCOUNT_DB])
    
import pages.database
@app.route('/pages/database', methods=['POST', 'GET'])
@app.route('/pages/database.<fn>', methods=['POST', 'GET'])
def _pages_database(fn=None):
    return application.response(request, pages.database.Page, fn, [POSTGRES, ACCOUNT_DB])

import pages.database_add
@app.route('/pages/database_add', methods=['POST', 'GET'])
@app.route('/pages/database_add.<fn>', methods=['POST', 'GET'])
def _pages_database_add(fn=None):
    return application.response(request, pages.database_add.Page, fn, [POSTGRES, ACCOUNT_DB])
             
import pages.database_sql
@app.route('/pages/database_sql', methods=['POST', 'GET'])
@app.route('/pages/database_sql.<fn>', methods=['POST', 'GET'])
def _pages_database_sql(fn=None):
    return application.response(request, pages.database_sql.Page, fn, [POSTGRES, ACCOUNT_DB])

import pages.oracle_monitor
@app.route('/pages/oracle_monitor', methods=['POST', 'GET'])
@app.route('/pages/oracle_monitor.<fn>', methods=['POST', 'GET'])
def _pages_oracle_monitor(fn=None):
    return application.response(request, pages.oracle_monitor.Page, fn, [POSTGRES, ACCOUNT_DB])
   
import pages.organizations
@app.route('/pages/organizations', methods=['POST', 'GET'])
def _pages_organizations():
    return application.response(request, pages.organizations.Page, None, [POSTGRES])
@app.route('/pages/organizations.<fn>', methods=['POST', 'GET'])
def _pages_organizations_fn(fn):
    return application.response(request, pages.organizations.Page, fn, [POSTGRES])
   
import pages.organization
@app.route('/pages/organization', methods=['POST', 'GET'])
def _pages_organization():
    return application.response(request, pages.organization.Page, None, [POSTGRES])
@app.route('/pages/organization.<fn>', methods=['POST', 'GET'])
def _pages_organization_fn(fn):
    return application.response(request, pages.organization.Page, fn, [POSTGRES])
 
import pages.organization_add
@app.route('/pages/organization_add', methods=['POST', 'GET'])
def _pages_organization_add():
    return application.response(request, pages.organization_add.Page, None, [POSTGRES])
@app.route('/pages/organization_add.<fn>', methods=['POST', 'GET'])
def _pages_organization_add_fn(fn):
    return application.response(request, pages.organization_add.Page, fn, [POSTGRES])
  
import pages.servers
@app.route('/pages/servers', methods=['POST', 'GET'])
def _pages_servers():
    return application.response(request, pages.servers.Page, None, [POSTGRES])
@app.route('/pages/servers.<fn>', methods=['POST', 'GET'])
def _pages_servers_fn(fn):
    return application.response(request, pages.servers.Page, fn, [POSTGRES])

import pages.departments
@app.route('/pages/departments', methods=['POST', 'GET'])
def _pages_departments():
    return application.response(request, pages.departments.Page, None, [POSTGRES])
@app.route('/pages/departments.<fn>', methods=['POST', 'GET'])
def _pages_departments_fn(fn):
    return application.response(request, pages.departments.Page, fn, [POSTGRES])
   
import pages.department
@app.route('/pages/department', methods=['POST', 'GET'])
def _pages_department():
    return application.response(request, pages.department.Page, None, [POSTGRES])
@app.route('/pages/department.<fn>', methods=['POST', 'GET'])
def _pages_department_fn(fn):
    return application.response(request, pages.department.Page, fn, [POSTGRES])
      
import procs.load_depts
@app.route('/procs/load_depts', methods=['POST', 'GET'])
@app.route('/procs/load_depts.<fn>', methods=['POST', 'GET'])
def _procs_load_depts(fn=None):
    return application.response(request, procs.load_depts.Page, fn, [POSTGRES])

import procs.cleaning
@app.route('/procs/cleaning', methods=['POST', 'GET'])
@app.route('/procs/cleaning.<fn>', methods=['POST', 'GET'])
def _procs_cleaning(fn=None):
    return application.response(request, procs.cleaning.Page, fn, [POSTGRES])
         
import responses.reg_server
@app.route('/reg_server', methods=['POST', 'GET'])
def _reg_server(): 
    return application.response(request, responses.reg_server.Response, None, [POSTGRES])
@app.route('/reg_server.<fn>', methods=['POST', 'GET'])
def _reg_server_fn(fn):
    return application.response(request, responses.reg_server.Response, fn, [POSTGRES])
            
import pages.request_log_record
@app.route('/pages/request_log_record', methods=['POST', 'GET'])
def _pages_request_log_record(): 
    return application.response(request, pages.request_log_record.Page, None, [POSTGRES])
@app.route('/pages/request_log_record.<fn>', methods=['POST', 'GET'])
def _pages_request_log_record_fn(fn): 
    return application.response(request, pages.request_log_record.Page, fn, [POSTGRES])
       
import pages.request_log
@app.route('/pages/request_log', methods=['POST', 'GET'])
def _pages_request_log(): 
    return application.response(request, pages.request_log.Page, None, [POSTGRES])
@app.route('/pages/request_log.<fn>', methods=['POST', 'GET'])
def _pages_request_log_fn(fn): 
    return application.response(request, pages.request_log.Page, fn, [POSTGRES])
                   
import responses.show_file
@app.route('/show_file', methods=['POST', 'GET'])
def _responses_show_xml_file(): 
    return application.response(request, responses.show_file.Response, None, [POSTGRES])
@app.route('/show_file.<fn>', methods=['POST', 'GET'])
def _responses_show_xml_file_fn(fn):
    return application.response(request, responses.show_file.Response, fn, [POSTGRES])
     
import pages.settings
@app.route('/pages/settings', methods=['POST', 'GET'])
@app.route('/pages/settings.<fn>', methods=['POST', 'GET'])
def _pages_settings(fn = None): 
    return application.response(request, pages.settings.Page, fn)
 
#import pages.sysadmin
#@app.route('/pages/sysadmin', methods=['POST', 'GET'])
#@app.route('/pages/sysadmin.<fn>', methods=['POST', 'GET'])
#def _pages_sysadmin(fn = None): 
#    return application.response(request, pages.sysadmin.Page, fn)
              
def navbar(page):    
    nav = page.navbar()
    nav.header(f'{application.module_name}, версия {application.version}', 'pages/start_page')
    nav.item('Пользователи', 'pages/users')
    nav.item('Подразделения', 'pages/departments')
    nav.item('Организации', 'pages/organizations')
    nav.item('Модули', 'pages/modules')
    nav.item('Журналы', 'pages/request_log')

application['navbar'] = navbar

