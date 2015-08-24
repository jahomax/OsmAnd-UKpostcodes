# OsmAnd-UKpostcodes
Set of scripts to create UK-postcodes files for OsmAnd.

Here are a few scripts to create either:
- a POI postcode file for the United Kingdom, being England, Northern Ireland, Scotland and Wales.
- or a postcode address files per country: one for England, for Scotland, for Northern-Ireland and for Wales.

Note that the scripts do not contain the final OsmAndMapCreator step. I leave that up to you (for now). For the POI file you only need to create a POI index. For the address file(s) you need to create a map and address index.



With regard to the generated files.<br> 
= POI postcode file United-Kingdom_postcodes_poi_europe.obf<br>
Simply search for one of the 1.7 million postcodes in the UK via POI search.
The Postcodes are stored as user_defined -> postal_code. If you want to display them (always) on the map, use that POI filter.


= \<Country\>_postcodes_address_europe.obf<br>
Since early 2015 or so OsmAnd can work with addresses (housenumbers) without a street. This makes it possible to use (or actually to fake) the postcode as housenumber. That's exactly what has been done with the address files. You can either:
- search on a postcode in a city/neighborhood as if it is a housenumber without street
- and directly as postcode as a "Search more villages/postcode" like in all other address files.

If you know that a postcode is somewhere in a city or suburb, you can select that city and all postcodes will appear. If you don't know the city, you can directly search for the postcode from the address screen. When you start typing, and the "city name" is not in the index, you get the "Search more villages/postcode".

Note that not all postcodes have a city assigned (about 56.000). This means that:
- Some postcodes can't be found by city, even though you know it is in that city.
- the total number of postcodes in the combined address files are roughly 1500 less (on 1.7 million) compared to the postcode_poi file as they simply can't be assigned. This might change in the future but this data is currently not available.

Requirements Linux/OS X/BSD: unzip, wget and sqlite3. Use your favorite package manager.
