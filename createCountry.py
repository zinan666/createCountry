# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import csv
import json
import os, sys
import argparse
from MySQLdb import Warning
from MySQLdb.cursors import SSCursor
import sqlite3
from pathlib import Path
from countryinfo import CountryInfo

sys.path.append(os.path.dirname(os.path.realpath(__file__)).replace("/dlatk/tools",""))
from dlatk.mysqlmethods import mysqlMethods as mm
from dlatk.mysqlmethods import mysqlMethods as sm

from warnings import filterwarnings
filterwarnings('ignore', category = Warning)

DEFAULT_DB_FROM = ''
DEFAULT_DB_TO = ''
DEFAULT_TABLE = ''
DEFAULT_CSV_FILE = ''
DEFAULT_JSON_FILE = ''
COUNTRY = ''

def createCountry(from_database, to_database, table, country):
    dbConn, dbCursor, dictCursor = mm.dbConnect(from_database)
    dbToConn, dbToCursor, dictToCursor = mm.dbConnect(to_database)

    stateInformation = ''
    province = CountryInfo(country).provinces()

    for i in province:
        temp = i.replace(' and ','%')
        temp = temp.replace(' de ','%')
        temp = temp.replace('City of ','')
        if temp == country:
            temp = temp+'%'+temp
        if temp == 'York':
            temp = 'York, UK'
        if i == province[0]:
            stateInformation += 'CASE WHEN a.location LIKE "%%%s%%" THEN "%s" '%(temp,i)
        elif i == province[-1]:
            stateInformation += 'WHEN a.location LIKE "%%%s%%" THEN "%s" END AS state'%(temp,i)
        else:
            stateInformation += 'WHEN a.location LIKE "%%%s%%" THEN "%s" '%(temp,i)

    state_id = ''

    for i in range(len(province)):
        temp = province[i].replace(' and ','%')
        temp = temp.replace(' de ','%')
        temp = temp.replace('City of ','')
        if temp == country:
            temp = temp+'%'+temp
        if temp == 'York':
            temp = 'York, UK'
        if i == 0:
            state_id += 'CASE WHEN a.location LIKE "%%%s%%" THEN %i '%(temp,i+1)
        elif i == len(province)-1:
            state_id += 'WHEN a.location LIKE "%%%s%%" THEN %i END AS state_id'%(temp,i+1)
        else:
            state_id += 'WHEN a.location LIKE "%%%s%%" THEN %i '%(temp,i+1)


    columnDescription = '(message_id bigint(20), user_id bigint(20), message text, created_at_utc datetime, state varchar(256), state_id int(6), lang varchar(4))'
    country = country.replace(' ','_')
    table_name = country+'_geotagged'
    dbToCursor.execute("""SHOW TABLES LIKE '{table}'""".format(table=table_name))
    tables = [item[0] for item in dbToCursor.fetchall()]
    if not tables:
        createSQL = """CREATE TABLE {table} {colDesc}""".format(table=table_name, colDesc=columnDescription)
        dbToCursor.execute(createSQL)

    createCountry1 = """
    INSERT INTO {to_db}.{to_table}
    SELECT * FROM
      (SELECT message_id, user_id, message, created_at_utc, {state}, {state_id}, message_lang AS lang
      FROM (SELECT message_id, user_id, message, created_at_utc, user_location AS location, message_lang 
            FROM {from_table} WHERE user_location IS NOT NULL) AS a) AS b
    WHERE b.state IS NOT NULL
    """.format(to_db=to_database,to_table=table_name, state=stateInformation,state_id=state_id,from_table=table)

    createCountry2 = """
    INSERT INTO {to_db}.{to_table}
    SELECT * FROM
      (SELECT message_id, user_id, message, created_at_utc, {state}, {state_id}, message_lang AS lang
      FROM (SELECT message_id, user_id, message, created_at_utc, tweet_location AS location, message_lang 
            FROM {from_table} WHERE user_location IS NULL AND tweet_location IS NOT NULL) AS a) AS b
    WHERE b.state IS NOT NULL
    """.format(to_db=to_database,to_table=table_name, state=stateInformation,state_id=state_id,from_table=table)

    dbCursor.execute(createCountry1)
    dbCursor.execute(createCountry2)

    return

def main():

    parser = argparse.ArgumentParser(description='Create tables for countries')
    # MySQL flags
    parser.add_argument('-fd', '--from_database', dest='fdb', default=DEFAULT_DB_FROM, help='MySQL database where tweets from.')
    parser.add_argument('-td', '--to_database', dest='tdb', default=DEFAULT_DB_TO, help='MySQL database where tweets will be stored.')
    parser.add_argument('-t', '--table', dest='table', default=DEFAULT_TABLE, help='MySQL table name.')

    # other flags
    parser.add_argument('--c', dest='country', default=COUNTRY, help='Country name.')


    args = parser.parse_args()
    createCountry(args.fdb, args.tdb, args.table, args.country)


if __name__ == "__main__":
    main()
    sys.exit(0)

