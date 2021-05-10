# createCountry

## Description

This script is to geotag tweets for a certain country. There are four input parameters. "from_database" is the name of the database where the source tables exist. "to_database" is the name of the database where target tweets go. "table" is the name of source tables in from_database. "country" is the name of target country. The name of generated table will be "country_geotagged" (e.g., United_States_geotagged, Italy_geotagged). If the generated table doesn't exist in to_database, it will create a new table automatically. And if the table exists, it will append the tweets to existing table. 

There will be eleven columns in generated tables. "user_id","message_id","message","created_at_utc","state","state_id", "county", "county_id", "city", "city_id", "postal_code", "lang".

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


## Install

To use createCountry, install package countryinfo firstly

```pip install countryinfo```

## Standalone Script

```.dlatk/tools/createCountry.py -fd from_database -td to_database -t table --c country```

For example

```.dlatk/tools/createCountry.py -fd coronavirus_msgs -td langofcovid -t messages_2020_03 --c 'Italy'```


