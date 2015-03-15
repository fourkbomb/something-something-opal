#!/usr/bin/env python3
import tornado.ioloop
import tornado.web
import argparse
import psycopg2
import momoko
import json

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        with open('index.html') as f:
            self.write(f.read())
# TODO move this stuff into individual files
class ListStopsHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, path):
        # TODO apparently PGSQL has a "citext" data type which will remove the necessity of all the lower()s
        if path.startswith('id/'):
            path = path[3:]
            self.application.db.execute("SELECT * FROM stops WHERE id = \'" + path.replace("\'", "\'\'").lower() + "\' LIMIT 1", callback=self._done_id)
        else:
            self.application.db.execute("SELECT id,name FROM stops WHERE position(\'"+ path.replace("\'", "\'\'").lower() +"\' in lower(name)) <> 0 ORDER BY name LIMIT 10", callback=self._done)

    def _done(self, cursor, error):
        fixed = {}
        for i in cursor.fetchall():
            fixed[i[1]] = i[0]
        self.write(fixed)
        self.finish()
    def _done_id(self, cursor, error):
        res = cursor.fetchall()[0]
        # order is id name lat long parent_station wheelchair_boarding platform_code
        self.write({
            'id': res[0],
            'name': res[1],
            'lat': str(res[2]),
            'long': str(res[3]),
            'parent': res[4],
            'wheelchair': int(res[5]),
            'platform': res[6]
        })
        self.finish()

app = tornado.web.Application([
    (r'/', IndexHandler),
    (r'/api/stops/(.*)', ListStopsHandler)
], static_path='static')

app.db = momoko.Pool(
    dsn='dbname=gtfs user=someone password=top_secret host=localhost port=5432',
    size=1
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=8080,
                        help='port to listen on')
    args = parser.parse_args()

    print("Starting server on :{}".format(args.port))
    app.listen(args.port)
    tornado.ioloop.IOLoop.instance().start()

# vim: set ts=4 et
