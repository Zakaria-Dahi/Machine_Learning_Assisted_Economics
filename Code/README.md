# Quick Description

This project allows to download information from INE and update it.

## Tools:

* `map_cli.py`: generate a PNG file with a map with some data (`python map_cli.py --help` for all the options).
* `map_gif.py`: generate a GIF file with a map with some data (`python map_gif.py --help` for all the options).

## Database structure (Original):

**TL;DR:** *Given a place from `locations` (for example `Málaga`) and a data serie from `series` (for example 
`male unemployment percentage`), you can found the data about it in `values` using the `id` found in `codes`. Also `codes`
contains information about when these data was obtained which allows to request new data to the INE DB.*

* `locations` table: Places considered in our study (`id` and `name` of the place). Currently, we are considering only 
provinces.
* `series` table: Data series store in our database, for example, employment data (`id`, `names`of the data serie, 
internal INE `code` for this serie and some description `text`about it).
* `codes` table: Given a place from `location` and a serie from `series`, it stores the internal INE `code` to access 
this information, when it was updated (`last_update` for the date in INE DB and `real_date` for the date when our program
gets those data). It also includes an `id` and a description `text`
* `values` table: Actual `value`s for a pair <place (from `locations`), serie (frome `series`)>. These data are annotated 
with their `year` and `period` (the meaning of the period value can be a month, a semester, a quarter...).

## Reduced Database structure:

FILE: `db-reduced.db`

A single table with clean data:
* Only series with data for all locations (33 series and 52 cities)
* Complete and consecutive years from 2003 to 2017 (15 years)
* 12 values per year (33 x 52 x 15 x 12 = 308 880 values)

## Main Python Files

* `database.py`: This file contains the python declaration for the database (ORM system using `SQLAlchemy`). The method 
`createDB` create/open the SQLite database `db.db` returning an object to manipulate it.
* `data.py`: This is the main program to get the actual data from INE database.

## Other Python Files

* `test.py`: Testing some operations over the database.
* `testURL.py`: Get all series in INE database
* `newSerie.py`: From a previous analysis (reduced one) generates the `series.json`to be downloaded.
* `cleanData.py`: Generate a clean version of the data (`db-reduced.db`)

## Other Files:

* `locations.sql`: SQL sentences for creating and population `localtions` table.
* `series.json`: Data needed to query INE Database for the interested series.
* `only-locs.db`: SQLite Database only including the locations (for a clean restarting).
* `db.db`: Current SQLite Database.
* `URL_analysis?.txt`: All the data series including a city.
* `URL_analysis?_reduced.txt`: Series selected from `URL_analysis?.txt` (only includes the number of INE series and the 
name of the series removing the city name). 

## Map

Undocumented.

## How to get a new series

To get the for some series:
* Search the series in `URL_analysis.txt` (this is the result of `textURL.py`).
* You have to include in `series.json` a new element with three values:
  * `name`: This is the name of the series (This is only information for the user)
  * `code`: This is the number which appears in the line `Searching in X`
  * `text`: This is the text removing the name of the location


