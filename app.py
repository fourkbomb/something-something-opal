#!/usr/bin/env python3
import tornado.ioloop
import tornado.web
import argparse
import psycopg2
import momoko
import json

from distance_matrix import DistanceMatrix

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        with open('index.html') as f:
            self.write(f.read())


# TODO move this stuff into individual files
class ListStopsHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, path):
        # TODO apparently PGSQL has a "citext" data type which will remove the
        # necessity of all the lower()s
        self.application.db.execute(
            "SELECT name, id FROM stops WHERE position(%s in lower(name)) <> 0"
            " ORDER BY name LIMIT 10",
            (path.lower(),), callback=self._done
        )

    def _done(self, cursor, error):
        fixed = dict(cursor)
        self.write(fixed)
        self.finish()


class GetStopHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, path):
        self.application.db.execute("SELECT * FROM stops WHERE id = %s LIMIT 1",
                                    (path,), callback=self._done)

    def _done(self, cursor, error):
        res = cursor.fetchone()
        if res:
            # order is id, name, lat, long, parent_station, wheelchair_boarding
            # platform_code
            response = {
                'id': res[0],
                'name': res[1],
                'lat': str(res[2]),
                'long': str(res[3]),
                'parent': res[4],
                'wheelchair': int(res[5]),
                'platform': res[6]
            }
            stopId = response['id']
            if stopId.startswith('CR_') or stopId.startswith('PST'):
                response['type'] = 'train'
            elif len(stopId) == 5:
                response['type'] = 'ferry'
            else:
                response['type'] = 'bus' # bus + light rail are the same.
            self.write(response)
        else:
            self.set_status(404)
            self.write({})
        self.finish()


# TODO move this into a generic "OpalCostHandler"
# Factor in other ticket types, only doing adult, peak atm.
# This is more of a proof of concept...
class OpalTrainCostHandler(tornado.web.RequestHandler):
    def get(self):
        from_station = self.get_argument('from_station')
        to_station = self.get_argument('to_station')
        
        dm = DistanceMatrix(config['google_server_api_key'])
        distance = dm.distance(from_station, to_station) / 1000

        cost = 8.30
        if distance <= 10:
            cost = 3.38
        elif distance <= 20:
            cost = 4.20
        elif distance <= 35:
            cost = 4.82
        elif distance <= 65:
            cost = 6.46

        self.write({'cost': cost})


# I'm sure there's a better way to do this
class KeyHandler(tornado.web.RequestHandler):
    def get(self):
        self.write({'key': config['google_browser_api_key']})


app = tornado.web.Application([
    (r'/', IndexHandler),
    (r'/api/stops/id/(.*)', GetStopHandler),
    (r'/api/stops/(.*)', ListStopsHandler),
    (r'/api/key', KeyHandler),
    (r'/api/cost/opal/train', OpalTrainCostHandler)
], static_path='static')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=8080,
                        help='port to listen on')
    parser.add_argument('-c', '--config', type=str, default='config.json',
                        help='location of config file')
    args = parser.parse_args()

    try:
        with open(args.config) as f:
            config = json.load(f)
    except:  # TODO: Specify exception to save from suciding self in future?
        raise Exception("Failed to load config file.")

    app.db = momoko.Pool(
        dsn=('dbname=gtfs user={db_user} password={db_pass} host={db_host} port={db_port}'
             ).format_map(config),
        size=1
    )
    print("Starting server on :{}".format(args.port))
    app.listen(args.port)
    tornado.ioloop.IOLoop.instance().start()

# vim: set ts=4 et
