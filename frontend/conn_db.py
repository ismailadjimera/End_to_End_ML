# =========================================
# Authentification management
# Inspired from Sven Bo via code is fun
# =========================================

import os

from deta import Deta  # pip install deta
from dotenv import load_dotenv  # pip install python-dotenv

import psycopg2
import pandas as pd

load_dotenv(".env")
DETA_KEY = os.getenv("DETA_KEY")

# Here you want to change your database, username & password according to your own values
param_dic = {
    "host"      : os.getenv("host"),
    "database"  : os.getenv("database"),
    "user"      : os.getenv("user"),
    "password"  : os.getenv("password")
}
def connect(params_dic):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params_dic)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        sys.exit(1) 
    return conn

def single_insert(conn, insert_req):
    """ Execute a single INSERT request """
    cursor = conn.cursor()
    try:
        cursor.execute(insert_req)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 1
    cursor.close()

# Connecting to the database
conn = connect(param_dic)