#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Version 1.0, 201607, Harry van der Wolf

# It requires roughly 2.5 GB to work on the temporary files
# Requirements: osmconvert, osmfilter, zlib-dev

import os, sys, platform, csv, sqlite3, zipfile
try:
        # For python3
        from urllib.request import urlopen
        python3 = "YES"
except ImportError:
        # Use python2
        from urllib2 import urlopen
        python3 = "NO"

#######################################################################
# Initialize file paths
realfile_dir  = os.path.dirname(os.path.abspath(__file__))

# Use dictionary for our variables
var_dict = {}
var_dict['TOOLSDIR'] = os.path.join(realfile_dir, "tools")
var_dict['WORKDIR'] = os.path.join(realfile_dir, "workfiles")
if not os.path.exists(var_dict['WORKDIR']):
    os.makedirs(var_dict['WORKDIR'])


OSplatform = platform.system()
# check if the osmc tools exist
if OSplatform == "Windows":
	var_dict['OSMCONVERT'] = os.path.join(var_dict['TOOLSDIR'], "osmconvert.exe")
	var_dict['OSMFILTER'] = os.path.join(var_dict['TOOLSDIR'], "osmfilter.exe")
else:
	var_dict['OSMCONVERT'] = os.path.join(var_dict['TOOLSDIR'], "osmconvert")
	var_dict['OSMFILTER'] = os.path.join(var_dict['TOOLSDIR'], "osmfilter")

#######################################################################
# Download the postcode files
url = "http://www.doogal.co.uk/files/"
pc_file = "PostcodeDistrictsSplit.csv"
print("\n\n== Downloading " + url + pc_file + " ==");
full_url = urlopen( url + pc_file )
with open( os.path.join(var_dict['WORKDIR'], pc_file),'wb') as output:
	output.write(full_url.read())

pc_file = "postcodes.zip"
print("\n\n== Downloading " + url + pc_file + " ==");
full_url = urlopen( url + pc_file )
with open( os.path.join(var_dict['WORKDIR'], pc_file),'wb') as output:
	output.write(full_url.read())
# unzip second one
print("\n\n== Unzipping " + pc_file + " ==");
fh = open( os.path.join(var_dict['WORKDIR'], pc_file), 'rb')
zfh = zipfile.ZipFile(fh)
for name in zfh.namelist():
    outfile = open( os.path.join(var_dict['WORKDIR'], name), 'wb')
    outfile.write(zfh.read(name))
    outfile.close()
fh.close()

#######################################################################
# Create database
DB_file = os.path.join( var_dict['WORKDIR'], "UK_postcodes.db" )
print('\n\n== First dropping and then creating the database ' + DB_file + ' ==')
# First drop existng one if exists
if os.path.isfile(DB_file):
	os.remove(DB_file)
connection = sqlite3.connect(DB_file)
connection.text_factory = str  # allows utf-8 data to be stored
cursor = connection.cursor()
# create tables
cursor.execute('create table PostcodeDistrictsSplit(prefix_pc text, town text)')
cursor.execute('create table mypostcodes(Postcode text primary key, Latitude float, Longitude float, City text, County text, Country text, IsoCountry text)')
sql = 'create table doogalpostcodes(Postcode text primary key, InUse text, Latitude float, Longitude float, Easting integer, Northing integer, GridRef text, '
sql += 'County text, District text, Ward text, DistrictCode text, WardCode text, Country text, CountyCode text, Constituency text, Introduced text, Terminatedd text, '
sql += 'Parish text, NationalPark text, Population text, Households text, Built_up_area text, Built_up_sub_division text, Lower_layer_super_output_area text, '
sql += 'Rural_urban text, Region text, Altitude integer, London_zone text, LSOA_Code text, Local_authority text,MSOA_Code text,Middle_layer_super_output_area text)'
cursor.execute(sql)
connection.commit()

## https://tentacles666.wordpress.com/2014/11/14/python-creating-a-sqlite3-database-from-csv-files/
# doogal'spostcodedistrictsplit
print('\n\n== importing the PostcodeDistrictsSplit.csv ==')
csvfile = open( os.path.join(var_dict['WORKDIR'], "PostcodeDistrictsSplit.csv") )
creader = csv.reader(csvfile, delimiter=',')
for t in creader:
	cursor.execute('INSERT INTO PostcodeDistrictsSplit VALUES (?,?)', t )
csvfile.close()
connection.commit()
# Cleanup
os.remove( os.path.join(var_dict['WORKDIR'], "PostcodeDistrictsSplit.csv") )
# doogal's postcodes
print('\n\n== importing the postcodes.csv ==')
csvfile = open( os.path.join(var_dict['WORKDIR'], "postcodes.csv") )
creader = csv.reader(csvfile, delimiter=',')
for t in creader:
	cursor.execute('INSERT INTO doogalpostcodes VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', t )
csvfile.close()
connection.commit()
# Clean up
os.remove( os.path.join(var_dict['WORKDIR'], "postcodes.zip") )
os.remove( os.path.join(var_dict['WORKDIR'], "postcodes.csv") )


#Now do the rest: remove "old" data and prepare for export
print('\n\n== Do all the data manipulation ==')
cursor.execute('delete from doogalpostcodes where InUse = "No"')
cursor.execute('delete from PostcodeDistrictsSplit where rowid not in (select min(rowid) from PostcodeDistrictsSplit group by prefix_pc)')
cursor.execute('Update PostcodeDistrictsSplit set prefix_pc=(prefix_pc || " ") where length(prefix_pc)=3')
cursor.execute('insert into mypostcodes(Postcode,Latitude,Longitude,City,County,Country) select dpc.postcode, dpc.latitude, dpc.longitude, trim(PCDS.town), trim(dpc.county), trim(dpc.country) from doogalpostcodes dpc left join PostcodeDistrictsSplit PCDS on PCDS.prefix_pc=substr(dpc.postcode,1,4)')
cursor.execute('update mypostcodes set IsoCountry="UK"')
connection.commit()
cursor.execute('drop table doogalpostcodes')
cursor.execute('vacuum')
connection.commit()
connection.close()

print('\n\n== Done importing! Now continueing with the export to OSM files for OsmAndMapCreator ==\n\n')

#####################################################################
# Create the postcode POI file
DB_file = os.path.join( var_dict['WORKDIR'], "UK_postcodes.db" )
connection = sqlite3.connect(DB_file)
connection.text_factory = str  # allows utf-8 data to be stored
cursor = connection.cursor()

file_name = os.path.join( var_dict['WORKDIR'], "UK_postcodes_poi_europe.osm" )
txt_file = open(file_name, 'w')
# First write the header
txt_file.write("<?xml version='1.0' encoding='UTF-8'?>")
txt_file.write("<osm version=\"0.6\" generator=\"osmfilter 1.4.0\">")
txt_file.write("	<bounds minlat=\"49.7\" minlon=\"-10.9\" maxlat=\"61.35131\" maxlon=\"2.0\"/>")

print("\n\n== Creating the POI file UK_postcodes_poi_europe.osm ==")
# First write the postcodes that contain a city
sql = "select '<node id=\"-' || ROWID || '\" lon=\"' || mpc.longitude || '\" lat=\"' || mpc.latitude || '\" visible=\"true\">',"
sql += "'<tag k=\"name\" v=\"' || mpc.postcode || '\"/>', '<tag k=\"user_defined_other\" v=\"postcode\"/> </node>' from mypostcodes mpc"
csql = sql + " where city not null"
# fetch 1000 rows at a time
cursor.execute(csql)
while True:
	rows = cursor.fetchmany(1000)
	if not rows: break
	for row in rows:
		str_row = str(row)
		txt_file.write(str_row.replace("|"," ") + "\n")
# Now write the postcodes that don't contain a city
ncsql = sql + " where city is null"
cursor.execute(ncsql)
while True:
	rows = cursor.fetchmany(1000)
	if not rows: break
	for row in rows:
		str_row = str(row)
		txt_file.write(str_row.replace("|"," ") + "\n")
osm_file= open(file_name, 'a')
osm_file.write("\n</osm>\n")
osm_file.close()

# Close file and database connection
txt_file.close()
connection.close()

print("\n\n== Convert POI file")
os.system(var_dict['OSMCONVERT'] + " -v --hash-memory=400-50-2 " + file_name + " --out-pbf > " + file_name + ".pbf")

