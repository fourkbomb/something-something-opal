#!/bin/sh
DBNAME=gtfs
echo Creating $DBNAME db...
createdb $DBNAME 2>/dev/null
echo Done

echo Initialising tables
psql $DBNAME -c "CREATE TABLE stops (id text PRIMARY KEY, name text, lat decimal, long decimal, parent_station text, wheelchair_boarding numeric, platform_code text)" 2>/dev/null
#psql $DBNAME -c "CREATE TABLE shapes (id text, lat text, long text, sequence text, distance text)" 2>/dev/null
psql $DBNAME -c "CREATE TABLE stop_times (id text, arr text, dep text, stop text references stops(id), seq numeric, headsign text, pickup numeric, dropoff numeric, distance_travelled text)" 2>/dev/null
echo Done

echo Dumping CSV file
#cat stops.txt | awk -F dump_stops.awk | pgsql gtfs
#psql gtfs -c  \
SED="s/'\"/'/g"
TOTAL=`wc -l < stops.txt`
COMPLETED=0
DATA=`sed 's/ /\\\@/g' stops.txt`
for i in $DATA; do
	statement="`echo $i | sed 's/\\\@/ /g' | awk -f dump_stops.awk`"
	psql gtfs -c "$statement" >/dev/null
	printf "$((TOTAL--)) remaining\r"
	
done
echo Done.

#echo Importing \"shapes.txt\". This may take a while...
#psql $DBNAME -c "COPY shapes FROM '$(pwd | sed "s/'/''/g")/shapes.txt' DELIMITER ',' CSV HEADER"
#echo Done!

echo Importing \"stop_times.txt\". This may take a while...
psql $DBNAME -c "COPY stop_times FROM '$(pwd | sed "s/'/''/g")/stop_times.txt' DELIMITER ',' CSV HEADER"
echo Done!

psql $DBNAME -c "ALTER TABLE stop_times ADD name text"

echo "Populating unpopulated database rows... This will take a while..."
PYTHON=""
if which python3 2>&1 >/dev/null; then
	PYTHON=`which python3`
elif which python 2>&1 >/dev/null; then
	if python --version | grep 'Python 3' 2>&1 >/dev/null; then
		PYTHON=`which python`
	else
		echo "Couldn't find python v3! Check it's in your PATH pls"
		exit
	fi
fi
echo Using python3 at $PYTHON
$PYTHON prepare.py
