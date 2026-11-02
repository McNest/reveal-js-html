"""Serve the decks on this computer: http://localhost:8008/ opens index.html.

  python tools/serve.py          port 8008
  python tools/serve.py 8080     another port

Browsers won't fetch a deck's Markdown from file://, so the decks need a web
server. Python's own (python -m http.server) listens on every network address
and prints that as http://[::]:8008/. This one listens on this computer only,
prints the localhost address (Ctrl+click it in the VS Code terminal), serves
this repository whatever folder it is started from, and tells the browser not
to keep old copies, so a reload always shows the latest edit. Ctrl+C stops it.
"""

import functools
import http.server
import os
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
PORT = 8008


class Handler(http.server.SimpleHTTPRequestHandler):
    """Handler

    Args:
        http (SimpleHTTPRequestHandler): The HTTP request handler instance
    """

    def end_headers(self):
        # Always fetched afresh: an edited memes.md shows on the next reload
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


class Server(http.server.ThreadingHTTPServer):
    """Server

    Args:
        http (HTTPServer): The HTTP server instance
    """

    # On Windows, address reuse lets a second server share a busy port without
    # an error, and the browser gets whichever answers
    allow_reuse_address = os.name != "nt"


EXIT_MSG = "Port %d is in use: stop the other server, or run  python tools/serve.py %d"
SERVER_MSG = "Serving HTTP on localhost port %d (http://localhost:%d/) ..."


def main(port):
    """Main function to start the server"""
    try:
        server = Server(("127.0.0.1", port), functools.partial(Handler, directory=ROOT))
    except OSError:
        sys.exit(EXIT_MSG % (port, port + 1))
    print(SERVER_MSG % (port, port))
    with server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else PORT)
