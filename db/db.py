import json
from pathlib import Path
from sys import dont_write_bytecode
import pymysql
from datetime import datetime

parent_directory = str(Path().absolute())

with open(parent_directory + '/db/config.json') as config_file:
    config = json.load(config_file)
    # config_local = json.load(config_file)

with open(parent_directory + '/db/config_local.json') as config_file:
    config_local = json.load(config_file)
    # config = json.load(config_file)


def ftime():
    return datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')


class DB:

    def __init__(self, use_local_db=False) -> None:
        self.db_host = config['host']
        self.db_user = config['user']
        self.db_password = config['password']
        self.db_name = config['db_name']

        self.db_conn = None
        self.changes_table_name = 'changes'
        self.reasons_table_name = 'change_reasons'


    def set_connection(self):
        print("{}: connection with DB is UP".format(ftime()))
        self.db_conn = pymysql.connect(host = self.db_host, user = self.db_user, password = self.db_password, database = self.db_name)
        

    def close_connection(self):
        print("{}: connection with DB CLOSED".format(ftime()))
        if (not self.db_conn or self.db_conn.open != True):
            return None
        self.db_conn.close()

    
    def get_reasons(self, action):
        if (not self.db_conn or self.db_conn.open != True):
            self.set_connection()

        cursor = self.db_conn.cursor()
        cursor.execute("SELECT `reason`,`long_description` FROM `{0}` WHERE `action` = '{1}'".format(self.reasons_table_name, action))
        rows = [{item[0]:item[1]} for item in cursor.fetchall()]
        self.close_connection()
        return rows

    
    def update_changes_no_reason(self, changes_time, user, action, vendor, priority, dialpeer, country):
        if (not self.db_conn or self.db_conn.open != True):
            self.set_connection()

        args = locals()
        del args['self']
        cursor = self.db_conn.cursor()
        query = """INSERT INTO `changes` (changes_time, user, action, vendor, priority, dialpeer, country) 
                          VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}')""".format(
                            changes_time,
                            user,
                            action,
                            vendor,
                            priority,
                            dialpeer,
                            country
                          )
        try:
            print("{0}: New record added: '{1}'".format(ftime(), args))
            cursor.execute(query=query)
            self.db_conn.commit()
        except pymysql.err.Error as error:
            print("{0}: Failed to update record to database rollback: {1}".format(ftime(), error))
            self.db_conn.rollback()
        finally:
            self.close_connection()
            print()
