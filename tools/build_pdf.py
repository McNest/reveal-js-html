"""Rebuild the decks' PDFs after a change: the print version (?print-pdf),
one slide a page, saved where the title slide's "Download as PDF" points.

  python tools/build_pdf.py              every deck in DECKS
  python tools/build_pdf.py memes asg2   just those
  python tools/build_pdf.py --live-arj   with ARJ as published, not the clone

Serves this repository on this computer on a free port (as tools/serve.py
does), then has Microsoft Edge (or Chrome: set BROWSER to its path) print
each deck with tools/print_pdf.mjs, which needs Node 22 or later.

The decks load ARJ from its published address (ARJ_LIVE). When the ARJ
repository is cloned beside this one (ARJ_REPO), the pages are served with
that clone in its place, so ARJ changes not yet pushed are in the PDF too;
--live-arj prints with the published ARJ instead.

Run tools/version.py --write first, so the PDF's title slide has the new
version; tools/commit.py --pdf does both, then commits.
"""

import functools
import http.server
import io
import os
import subprocess
import sys
import threading

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

# deck name: (its folder, the PDF), relative to ROOT
DECKS = {
    "memes": ("docs/memes/", "docs/memes/src/pdf/memes.pdf"),
    "asg2": ("docs/asg2/", "docs/asg2/src/pdf/asg2.pdf"),
}

# The ARJ repository: C:/Users/user/GitHub/SDevTutors/apocalypse-reveal-js
ARJ_REPO = os.path.normpath(os.path.join(ROOT, "..", "..", "SDevTutors", "apocalypse-reveal-js"))
ARJ_LIVE = b"https://sdevtutors.github.io/apocalypse-reveal-js/"
ARJ_LOCAL = "/arj-local/"


class Handler(http.server.SimpleHTTPRequestHandler):
    """This repository, with /arj-local/ served from the ARJ clone and the
    published ARJ address in pages swapped for it"""

    arj = None  # the ARJ clone, or None for the published ARJ

    def translate_path(self, path):
        if self.arj and path.startswith(ARJ_LOCAL):
            rel = path[len(ARJ_LOCAL):].split("?")[0].split("#")[0]
            return os.path.join(self.arj, *rel.split("/"))
        return super().translate_path(path)

    def send_head(self):
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            path = os.path.join(path, "index.html")
        if self.arj and path.endswith((".html", ".md")) and os.path.isfile(path):
            with open(path, "rb") as file:
                body = file.read().replace(ARJ_LIVE, ARJ_LOCAL.encode())
            self.send_response(200)
            kind = "text/html" if path.endswith(".html") else "text/markdown"
            self.send_header("Content-Type", kind + "; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            return io.BytesIO(body)
        return super().send_head()

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *args):
        pass  # quiet: print_pdf.mjs reports each deck


def build(names, arj):
    """Print each deck named to its PDF; returns how many failed"""
    Handler.arj = arj
    server = http.server.ThreadingHTTPServer(
        ("127.0.0.1", 0), functools.partial(Handler, directory=ROOT)
    )
    threading.Thread(target=server.serve_forever, daemon=True).start()
    port = server.server_address[1]
    print("ARJ:", arj or ARJ_LIVE.decode())
    failed = 0
    try:
        for name in names:
            folder, pdf = DECKS[name]
            url = "http://localhost:%d/%s?print-pdf" % (port, folder)
            os.makedirs(os.path.dirname(os.path.join(ROOT, pdf)), exist_ok=True)
            done = subprocess.run(
                ["node", os.path.join(ROOT, "tools", "print_pdf.mjs"), url, os.path.join(ROOT, pdf)],
                check=False,
            )
            if done.returncode:
                print("  failed:", name)
                failed += 1
    finally:
        server.shutdown()
    return failed


def main(args):
    """Main method"""
    names = [a for a in args if not a.startswith("--")] or list(DECKS)
    unknown = [n for n in names if n not in DECKS]
    if unknown:
        sys.exit("No deck called %s: one of %s" % (", ".join(unknown), ", ".join(DECKS)))
    arj = None if "--live-arj" in args or not os.path.isdir(ARJ_REPO) else ARJ_REPO
    sys.exit(1 if build(names, arj) else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
