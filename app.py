#!/usr/bin/env python3
import tornado.ioloop
import tornado.web

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, World!")

application = tornado.web.Application([
    (r"/", MainHandler)
])

if __name__ == "__main__":
    application.listen(8080)
    tornado.ioloop.IOLoop.instance().start()

# vim: set ts=4 et
