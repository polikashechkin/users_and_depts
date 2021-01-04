import os, sys
from domino.core import log, Version
from domino.account import Account, find_account
from domino.databases.postgres import Postgres
from settings import MODULE_ID

import domino.tables.postgres.dictionary
import domino.tables.postgres.dept_param
import domino.tables.postgres.dept
import domino.tables.postgres.server 
import domino.tables.postgres.user
import domino.tables.postgres.grant
import domino.tables.postgres.request_log 
import domino.tables.postgres.organization

import procs.load
import procs.load_depts
import procs.cleaning

class MsgLog:
    def __init__(self, account_id):
        self.account_id = account_id
    def __call__(self, msg):
        print(msg)

if __name__ == "__main__":

    account_id = sys.argv[1]
    msg_log = MsgLog(account_id)
    
    #Postgres.create_database(account_id, msg_log)
    Postgres.on_activate(account_id, msg_log)

    domino.tables.postgres.user.on_activate(account_id, msg_log)
    domino.tables.postgres.grant.on_activate(account_id, msg_log)
    domino.tables.postgres.dictionary.on_activate(account_id, msg_log)
    domino.tables.postgres.dept_param.on_activate(account_id, msg_log)
    domino.tables.postgres.dept.on_activate(account_id, msg_log)
    domino.tables.postgres.server.on_activate(account_id, msg_log) 
    #domino.tables.postgres.request_log.on_activate(account_id, msg_log) 
    domino.tables.postgres.organization.on_activate(account_id, msg_log) 

    procs.load.on_activate(account_id, msg_log)
    procs.load_depts.on_activate(account_id, msg_log)
    procs.cleaning.on_activate(account_id, msg_log)
    
