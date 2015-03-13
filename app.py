#!/usr/bin/env python3
import tornado.ioloop
import tornado.web
import argparse

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, World!")

app= tornado.web.Application([
    (r"/", MainHandler)
])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', help="which port for the server", type=int)
    args = parser.parse_args()
    
    port = args.port or 8080
    print("Starting server on :{}".format(port))
    app.listen(port)
    tornado.ioloop.IOLoop.instance().start()

# vim: set ts=4 et
