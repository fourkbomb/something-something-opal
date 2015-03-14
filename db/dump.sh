#!/bin/sh
DBNAME=gtfs
echo Creating $DBNAME db...
createdb $DBNAME 2>/dev/null
echo Done

echo Initialising tables
psql $DBNAME -c "CREATE TABLE stops (id text PRIMARY KEY, name text, lat decimal, long decimal, parent_station text, wheelchair_boarding numeric, platform_code text)" 2>/dev/null
echo Done

echo Dumping CSV file
#cat stops.txt | awk -F dump_stops.awk | pgsql gtfs
#psql gtfs -c  \
SED="s/'\"/'/g"
TOTAL=`cat stops.txt | wc -l`
COMPLETED=0
DATA=`cat stops.txt | sed 's/ /\\\@/g'`
for i in $DATA; do
	statement="`echo $i | sed 's/\\\@/ /g' | awk -f dump_stops.awk`"
	psql gtfs -c "$statement" >/dev/null
	printf "$((TOTAL--)) remaining\r"
	
done
