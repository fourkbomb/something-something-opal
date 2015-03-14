#!/usr/bin/env python3
import tornado.ioloop
import tornado.web
import argparse

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        f = open('frontend/index.html', 'r')
        self.write(f.read())
        f.close()

app = tornado.web.Application([
    (r"/", IndexHandler),
    (r"/js/(.*)", tornado.web.StaticFileHandler, {'path': 'frontend/js'}),
    (r"/lib/(.*)", tornado.web.StaticFileHandler, {'path': 'frontend/lib'})
])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=8080,
                        help='port to listen on')
    args = parser.parse_args()

    print("Starting server on :{}".format(args.port))
    app.listen(args.port)
    tornado.ioloop.IOLoop.instance().start()

# vim: set ts=4 et
