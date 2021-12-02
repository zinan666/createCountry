# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import csv
import json
import os, sys
import argparse
import pandas as pd
import urllib
import urllib.request
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

country_dict = {'Andorra': 'AD', 'Argentina': 'AR', 'American Samoa': 'AS', 'Austria': 'AT', 'Australia': 'AU', 'Åland Islands': 'AX', 'Bangladesh': 'BD',
                'Belgium': 'BE', 'Bulgaria': 'BG', 'Bermuda': 'BM', 'Brazil': 'BR', 'Belarus': 'BY', 'Canada': 'CA', 'Switzerland': 'CH',
                'Colombia': 'CO', 'Costa Rica': 'CR', 'Czechia': 'C', 'German': 'DE', 'Denmark': 'DK', 'Dominican Republic': 'DO', 'Algeria': 'DZ',
                'Spain': 'ES', 'Finland': 'FI', 'Faroe Islands': 'FO', 'France': 'FR', 'United Kingdom of Great Britain and Northern Ireland': 'GB',
                'French Guiana': 'GF', 'Guernsey': 'GG', 'Greenland': 'GL', 'Guadeloupe': 'GP', 'Guatemala': 'GT', 'Guam': 'GU', 'Croatia': 'HR',
                'Hungary': 'HU', 'Ireland': 'IE', 'Isle of Man': 'IM', 'India': 'IN', 'Iceland': 'IS', 'Italy': 'IT', 'Jersey': 'JE', 'Japan': 'JP',
                'Liechtenstein': 'LI', 'Sri Lanka': 'LK', 'Lithuania': 'LT', 'Luxembourg': 'LU', 'Latvia': 'LV', 'Monaco': 'MC',
                'Republic of Moldova': 'MD', 'Marshall Islands': 'MH', 'The former Yugoslav Republic of Macedonia': 'MK',
                'Northern Mariana Islands': 'MP', 'Martinique': 'MQ', 'Malta': 'MT', 'Mexico': 'MX', 'Malaysia': 'MY', 'New Caledonia': 'NC',
                'Netherlands': 'NL', 'Norway': 'NO', 'New Zealand': 'NZ', 'Philippines': 'PH', 'Pakistan': 'PK', 'Poland': 'PL',
                'Saint Pierre and Miquelon': 'PM', 'Puerto Rico': 'PR', 'Portugal': 'PT', 'Réunion': 'RE', 'Romania': 'RO', 'Russian Federation': 'RU',
                'Sweden': 'SE', 'Slovenia': 'SI', 'Svalbard and Jan Mayen Islands': 'SJ', 'Slovakia': 'SK', 'San Marino': 'SM', 'Thailand': 'TH',
                'Turkey': 'TR', 'Ukraine': 'UA', 'United States of America': 'US', 'Uruguay': 'UY', 'Holy See': 'VA', 'United States Virgin Islands': 'VI',
                'Wallis and Futuna Islands': 'WF', 'Mayotte': 'YT', 'South Africa': 'ZA'}

html=urllib.request.urlopen('https://raw.githubusercontent.com/thampiman/reverse-geocoder/master/reverse_geocoder/rg_cities1000.csv').read().decode("utf-8")
cities = html.splitlines()


def createCountry(from_database, to_database, table, country):
    dbConn, dbCursor, dictCursor = mm.dbConnect(from_database)
    dbToConn, dbToCursor, dictToCursor = mm.dbConnect(to_database)

    country_abbr = country_dict[country]
    df = pd.Series(cities).to_frame()
    df = df.rename(columns={0:"original"})
    df['text'] = df['original'].apply(lambda x:x if ','+country_abbr in x else None)

    df = df[~df['text'].isnull()]
    df['city'] = df['text'].apply(lambda x:x.split(",")[2])
    df['state'] = df['text'].apply(lambda x:x.split(",")[3])
    df['county'] = df['text'].apply(lambda x:x.split(",")[4])
    df['country'] = df['text'].apply(lambda x:x.split(",")[5])
    df = df[['city','county','state','country']]

    df = df[df['country']==country_abbr]
    df = df.drop_duplicates()
    df.reset_index(inplace=True,drop=True)

    state_list = df['state'].value_counts().index
    stateInformation = ''
    for i in state_list:
        temp = i.replace(' and ','%')
        temp = temp.replace(' de ','%')
        if not i:
            continue
        if not stateInformation:
            stateInformation += 'CASE WHEN a.location LIKE "%%%s%%" THEN "%s" '%(temp,i)
        elif i == state_list[-1]:
            stateInformation += 'WHEN a.location LIKE "%%%s%%" THEN "%s" END AS state'%(temp,i)
        else:
            stateInformation += 'WHEN a.location LIKE "%%%s%%" THEN "%s" '%(temp,i)


    state_id = ''
    for i in range(len(state_list)):
        temp = state_list[i].replace(' and ','%')
        temp = temp.replace(' de ','%')
        if not state_list[i]:
            continue
        if not state_id:
            state_id += 'CASE WHEN a.location LIKE "%%%s%%" THEN %i '%(temp,i+1)
        elif i == len(state_list)-1:
            state_id += 'WHEN a.location LIKE "%%%s%%" THEN %i END AS state_id'%(temp,i+1)
        else:
            state_id += 'WHEN a.location LIKE "%%%s%%" THEN %i '%(temp,i+1)


    df_county = df.groupby(['county','state']).count().reset_index()
    countyInformation = ''
    county_id = ''
    for i in range(len(df_county)):
        temp = df_county.iloc[i]['county'].replace(' County','').replace(' and ','%').replace(' de ','%')
        county = df_county.iloc[i]['county']
        state = df_county.iloc[i]['state'].replace(' and ','%').replace(' de ','%')
        com = temp+'%'+state
        if not county or not state:
            continue
        if not countyInformation and not county_id:
            countyInformation += 'CASE WHEN a.location LIKE "%%%s%%" THEN "%s" '%(com,county)
            county_id += 'CASE WHEN a.location LIKE "%%%s%%" THEN "%s" '%(com,i+1)
        elif i == len(df_county)-1:
            countyInformation += 'WHEN a.location LIKE "%%%s%%" THEN "%s" END AS county,'%(com,county)
            county_id += 'WHEN a.location LIKE "%%%s%%" THEN "%s" END AS county_id,'%(com,i+1)
        else:
            countyInformation += 'WHEN a.location LIKE "%%%s%%" THEN "%s" '%(com,county)
            county_id += 'WHEN a.location LIKE "%%%s%%" THEN "%s" '%(com,i+1)


    df_city = df[['city','state']].drop_duplicates().reset_index(drop=True)
    cityInformation = ''
    city_id = ''
    for i in range(len(df_city)):
        temp = df_city.iloc[i]['city'].replace(' and ','%').replace(' de ','%')
        city = df_city.iloc[i]['city']
        state = df_city.iloc[i]['state'].replace(' and ','%').replace(' de ','%')
        com = temp+'%'+state
        if not city or not state:
            continue
        if not cityInformation and not city_id:
            cityInformation += 'CASE WHEN a.location LIKE "%%%s%%" THEN "%s" '%(com,city)
            city_id += 'CASE WHEN a.location LIKE "%%%s%%" THEN "%s" '%(com,i+1)
        elif i == len(df_city)-1:
            cityInformation += 'WHEN a.location LIKE "%%%s%%" THEN "%s" END AS city'%(com,city)
            city_id += 'WHEN a.location LIKE "%%%s%%" THEN "%s" END AS city_id'%(com,i+1)
        else:
            cityInformation += 'WHEN a.location LIKE "%%%s%%" THEN "%s" '%(com,city)
            city_id += 'WHEN a.location LIKE "%%%s%%" THEN "%s" '%(com,i+1)


    columnDescription = '(message_id bigint(20), user_id bigint(20), message text, created_at_utc datetime, state varchar(256), state_id int(6), county varchar(256), county_id int(6), city varchar(256), city_id int(6), postal_code int(5), lang varchar(4))'
    table_name = country_abbr+'_geotagged'
    dbToCursor.execute("""SHOW TABLES LIKE '{table}'""".format(table=table_name))
    tables = [item[0] for item in dbToCursor.fetchall()]
    if not tables:
        createSQL = """CREATE TABLE {table} {colDesc}""".format(table=table_name, colDesc=columnDescription)
        dbToCursor.execute(createSQL)

    createCountry1 = """
    INSERT INTO {to_db}.{to_table}
    SELECT * FROM
      (SELECT message_id, user_id, message, created_at_utc, {state}, {state_id}, {county}, {county_id}, {city}, {city_id}, postal_code, message_lang AS lang
      FROM (SELECT message_id, user_id, message, created_at_utc, user_location AS location, postal_code, message_lang 
            FROM {from_table} WHERE user_location IS NOT NULL) AS a) AS b
    WHERE b.state IS NOT NULL
    """.format(to_db=to_database,to_table=table_name,state=stateInformation,state_id=state_id,county=countyInformation if countyInformation else "(SELECT NULL) AS county",county_id=county_id if county_id else "(SELECT NULL) AS county_id",city=cityInformation,city_id=city_id,from_table=table)

    createCountry2 = """
    INSERT INTO {to_db}.{to_table}
    SELECT * FROM
      (SELECT message_id, user_id, message, created_at_utc, {state}, {state_id}, {county}, {county_id}, {city}, {city_id}, postal_code, message_lang AS lang
      FROM (SELECT message_id, user_id, message, created_at_utc, tweet_location AS location, postal_code,message_lang 
            FROM {from_table} WHERE user_location IS NULL AND tweet_location IS NOT NULL) AS a) AS b
    WHERE b.state IS NOT NULL
    """.format(to_db=to_database,to_table=table_name, state=stateInformation,state_id=state_id,county=countyInformation if countyInformation else "(SELECT NULL) AS county",county_id=county_id if county_id else "(SELECT NULL) AS county_id",city=cityInformation,city_id=city_id,from_table=table)

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

