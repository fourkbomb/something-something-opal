import psycopg2
import argparse
import json
import functools


@functools.lru_cache(maxsize=256)
def lookup_stop_name(id):
	cur = conn.cursor()
	cur.execute('SELECT parent_station FROM stops WHERE id=%s', (id,))
	res = cur.fetchone()[0]
	cur.close()
	return res

def set_names(id, name):
	cur = conn.cursor()
	cur.execute('UPDATE stop_times SET name=%s WHERE stop=%s', (name,id))
	res = cur.rowcount
	cur.close()
	return res

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

stop_times_ids = conn.cursor()

stop_times_ids.execute('SELECT DISTINCT stop FROM stop_times WHERE position(%s in stop) <> 0', ('CR_',))


# now we have a list of ids with train stations in them.
for i in stop_times_ids:
	name = lookup_stop_name(i[0])
	name = name.split(' Station')[0]
	#set_names()
	i=i[0]
	changed = set_names(i, name)
	conn.commit()
	print("set name in %d rows (id: %s name: %s)"%(changed,i,name))
print("Saving changes...")
stop_times_ids.close()
conn.commit()
print("Done!")
