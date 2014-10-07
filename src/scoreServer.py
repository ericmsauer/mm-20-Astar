#!/usr/bin/env python
import sys
import os
import BaseHTTPServer
import json
from vis.Scoreboard import Scoreboard
#from SimpleHTTPServer import SimpleHTTPRequestHandler

my_scoreboard = Scoreboard()

# makes sure only the visualizer will be found
class mmVisRequstHandler(BaseHTTPServer.BaseHTTPRequestHandler, object):
    def do_POST(self):
        content_len = int(self.headers.getheader('content-length', 0))
        post_body = self.rfile.read(content_len)
        try: 
            my_scoreboard.turn(post_body)
            self.send_response(200)
            self.end_headers()
        except ValueError, TypeError:
            self.send_response(400)
            self.end_headers()

    
## blow here is basic web server stuff
HandlerClass = mmVisRequstHandler
ServerClass  = BaseHTTPServer.HTTPServer
Protocol     = "HTTP/1.0"

def start_web_server():
    if sys.argv[1:]:
        port = int(sys.argv[1])
    else:
        port = 7000
    server_address = ('127.0.0.1', port)

    HandlerClass.protocol_version = Protocol
    httpd = ServerClass(server_address, HandlerClass)

    sa = httpd.socket.getsockname()
    print "Serving HTTP on", sa[0], "port", sa[1], "..."
    httpd.serve_forever()


def main():
    start_web_server()
    
if __name__=="__main__":
    main()

