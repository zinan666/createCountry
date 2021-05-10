# createCountry

## Description

This script is to geotag tweets for a certain country. There are four input parameters. "from_database" is the name of the database where the source tables exist. "to_database" is the name of the database where target tweets go. "table" is the name of source tables in from_database. "country" is the name of target country. The name of generated table will be "country_geotagged" (e.g., United_States_geotagged, Italy_geotagged). If the generated table doesn't exist in to_database, it will create a new table automatically. And if the table exists, it will append the tweets to existing table. 

There will be eleven columns in generated tables. "user_id","message_id","message","created_at_utc","state","state_id", "county", "county_id", "city", "city_id", "lang".

## Install

To use createCountry, install package countryinfo firstly

```pip install countryinfo```

## Standalone Script

```.dlatk/tools/createCountry.py -fd from_database -td to_database -t table --c country```

For example

```.dlatk/tools/createCountry.py -fd coronavirus_msgs -td langofcovid -t messages_2020_03 --c 'Italy'```

