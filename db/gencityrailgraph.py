#!/usr/bin/python3
import psycopg2
import argparse
import json

def get_distance_for_stop(tripid, seq):
	cur = conn.cursor()
	cur.execute('SELECT name,distance_travelled FROM stop_times WHERE id=%s AND seq=%s', (tripid,seq))
	res = cur.fetchone()
	if res == None:
		return (None,None)
	return (res[0],res[1])

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config', type=str, default='../config.json',
                        help='location of config file')
args = parser.parse_args()

config = {}

try:
    with open(args.config) as f:
        config = json.load(f)
except:  # TODO: Specify exception to save from suciding self in future?
    raise Exception("Failed to load config file.")
print("Establishing database connection...")
conn = psycopg2.connect('dbname=gtfs user={db_user} password={db_pass} host={db_host} port={db_port}'.format_map(config))
print("Connection established!")

stops = conn.cursor()

stops.execute('SELECT id,name FROM stops WHERE position(%s in id) <> 0', ('PST',))

graph = {}

def saveGraph():
	with open('graph.json', 'w') as f:
		json.dump(graph, f)

def display_progress(name, nameCur, nameTotal, cur, total):
	print("Finding stations adjacent to {} ({}/{}): {}/{}         ".format(name,nameCur,nameTotal,cur,total), end='\r')
nameTotal = stops.rowcount
nameCur = 0
for i in stops:
	nameCur += 1
	# dictionary of distances to nearest two nodes
	stop = i[0]
	#print("Finding stations adjacent to " + i[1], end='\r')
	name = i[1]
	display_progress(name, nameCur, nameTotal, 0, '???')
	distances = {}
	seen = []
	if stop in graph:
		distances = graph[stop]
	routes_with_stop = conn.cursor()
	routes_with_stop.execute('SELECT DISTINCT id,seq,distance_travelled FROM stop_times WHERE name=%s', (stop,))
	total = routes_with_stop.rowcount
	cur = 0
	for i in routes_with_stop:
		cur += 1
		display_progress(name, nameCur,nameTotal,cur, total)
		if (i[1],i[2]) in seen:
			continue
		seen.append((i[1],i[2]))
		if i[1] == 1:
			# no previous stop
			continue
		(prevname,prevdist) = get_distance_for_stop(i[0], i[1]-1)
		if prevname == None or prevdist == None:
			continue
		if prevname in distances:
			# already calculated
			continue
		prevdist = float(prevdist)
		mydist = float(i[2])
		distances[prevname] = abs(prevdist-mydist)
	#print(distances)
	graph[stop] = distances
	saveGraph()
	#raise Exception("done")

