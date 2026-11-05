"""Version numbers for this repository: each deck has its own, and so does
everything else (the list of decks, the readme, the tools), "site".

  python tools/version.py                   each one's version now, and next
  python tools/version.py --write memes     one more change to the meme bank:
                                            its new version and date on its
                                            title slide and in its page
  python tools/version.py --write asg2 site the same for each one named
  python tools/version.py --link [memes]    link "Version 1.8.3" on a deck's
                                            title slide to this repository on
                                            GitHub as it was at the commit
                                            that first published it

Which files belong to which: a deck is everything in its folder (BUCKETS);
"site" is everything else. tools/commit.py works this out from what has
changed, and gives each one its own commit.

A version is year.tenth.change:
  year    1 for 2026, 2 for 2027 ...
  tenth   which tenth of the year today falls in, 0 to 9 (days 1-36 are 0,
          20 October to 25 November is 8, and so on): about every 36 days
  change  one more for every change to that deck, back to 1 when a new
          tenth starts
So 1.8.12 is the meme bank's twelfth change between 20 October and 25
November 2026, and its next tenth starts at 1.9.1. Each --write is one
change: run it once for each change, before you commit (running it twice
counts two). The number is worked out from the version already written, so
it never goes down.

The title slide shows the month ("October 2026"); the page's metadata gets
the full date and time.

ARJ has its own version, worked out the same way by tools/version.py in the
ARJ repository (SDevTutors/apocalypse-reveal-js). --write memes or asg2 copies
it into the page's generator line from that repository's arj/js/deck-start.js,
when the repository is cloned where ARJ_REPO says.

--link: looks for the first commit whose file has this version, checks that
commit has been pushed, and only then links the version to the repository
as it was then (github.com/.../tree/SHA: browse the files at that point,
not the changes). Until then the version links to the list of commits, so
the slide never points at a commit that doesn't exist. Run it after you
push.
"""

import datetime
import os
import re
import subprocess
import sys
from urllib.parse import quote

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
# The ARJ repository: C:/Users/user/GitHub/SDevTutors/apocalypse-reveal-js
ARJ_REPO = os.path.normpath(
    os.path.join(ROOT, "..", "..", "SDevTutors", "apocalypse-reveal-js")
)
GITHUB = "https://github.com/McNest/reveal-js-html/"
FIRST_YEAR = 2026

TITLE_SLIDE = [
    (r'(<span class="deck-version">)[^<]*(</span>)', r"\g<1>{v}\g<2>"),
    (
        r'<time class="deck-date" datetime="[^"]*">[^<]*</time>',
        '<time class="deck-date" datetime="{stamp}">{month}</time>',
    ),
]
META_VERSION = [
    (r'<meta name="version" content="[^"]*" />', '<meta name="version" content="{v}" />')
]
META_DATES = [
    # dcterms, dc-terms, DCTERMS ...: whatever prefix the page declares
    (r'(<meta name="[A-Za-z-]+\.modified" content=")[^"]*(" />)', r"\g<1>{stamp}\g<2>"),
    (
        r'<meta property="article:modified_time" content="[^"]*" />',
        '<meta property="article:modified_time" content="{stamp}" />',
    ),
]

# name: its folder (None: everything that isn't a deck), the file whose
# version is read (the title slide), and the files to write
BUCKETS = {
    "memes": {
        "folder": "docs/memes/",
        "source": "docs/memes/memes.md",
        "old": ["memes.md"],  # where it was before, for --link
        "swaps": {
            "docs/memes/memes.md": TITLE_SLIDE,
            "docs/memes/index.html": META_VERSION + META_DATES,
        },
    },
    "asg2": {
        "folder": "docs/asg2/",
        "source": "docs/asg2/index.html",
        "swaps": {"docs/asg2/index.html": TITLE_SLIDE + META_VERSION + META_DATES},
    },
    "site": {
        "folder": None,
        "source": "index.html",
        "swaps": {"index.html": META_VERSION},
    },
}
# The pages that name the ARJ version they are built with
GENERATORS = ["docs/memes/index.html", "docs/asg2/index.html"]


def tenth(day):
    days = 366 if datetime.date(day.year, 12, 31).timetuple().tm_yday == 366 else 365
    return (day.timetuple().tm_yday - 1) * 10 // days


def version(today, last=None):
    """The next version after last: one more change in this tenth, or the
    first change of a new one."""
    year, part = today.year - FIRST_YEAR + 1, tenth(today)
    if last and last.startswith("%d.%d." % (year, part)):
        return "%d.%d.%d" % (year, part, int(last.split(".")[2]) + 1)
    return "%d.%d.1" % (year, part)


def written(name="memes"):
    """The version written for that deck (or "site") now."""
    text = open(os.path.join(ROOT, BUCKETS[name]["source"]), encoding="utf-8").read()
    found = re.search(r'<span class="deck-version">([^<]*)</span>', text) or re.search(
        r'<meta name="version" content="([^"]*)" />', text
    )
    return found.group(1) if found else None


def bucket_of(path):
    """Which deck a file belongs to, by its path from ROOT; "site" for the rest."""
    path = path.replace("\\", "/")
    for name, bucket in BUCKETS.items():
        if bucket["folder"] and path.startswith(bucket["folder"]):
            return name
    return "site"


def arj_version():
    """ARJ's version, from its repository's deck-start.js, or None."""
    path = os.path.join(ARJ_REPO, "arj", "js", "deck-start.js")
    if not os.path.exists(path):
        return None
    found = re.search(r"version: '([^']*)'", open(path, encoding="utf-8").read())
    return found and found.group(1)


def write(name):
    """One more change to that deck (or "site"): write its new version and
    date. Returns the new version."""
    now = datetime.datetime.now().astimezone().replace(microsecond=0)
    today = now.date()
    v = version(today, written(name))
    swaps = dict(BUCKETS[name]["swaps"])
    arj = arj_version()
    for page in GENERATORS:
        if arj and page in swaps:
            swaps[page] = swaps[page] + [
                (
                    r"and (?:TAP|ARJ) [0-9.]+, (?:The Apocalypse Plugin|Apocalypse Reveal-js)",
                    "and ARJ %s, Apocalypse Reveal-js" % arj,
                )
            ]
    for target, pairs in swaps.items():
        path = os.path.join(ROOT, target)
        text = open(path, encoding="utf-8", newline="").read()
        for pattern, template in pairs:
            new = template.format(v=v, stamp=now.isoformat(), month=today.strftime("%B %Y"))
            text, n = re.subn(pattern, new, text)
            if not n:
                print("  not found in", target, ":", pattern)
        open(path, "w", encoding="utf-8", newline="").write(text)
    return v


def main(args):
    """Main method"""
    names = [a for a in args if not a.startswith("--")]
    unknown = [n for n in names if n not in BUCKETS]
    if unknown:
        sys.exit("No deck called %s: one of %s" % (", ".join(unknown), ", ".join(BUCKETS)))
    if "--write" in args:
        if not names:
            sys.exit("Which one? python tools/version.py --write " + " | ".join(BUCKETS))
        for name in names:
            print("%-6s %s" % (name, write(name)))
        return
    today = datetime.date.today()
    for name in names or BUCKETS:
        now = written(name)
        print("%-6s %s, next %s" % (name, now, version(today, now)))
    print("ARJ    %s" % (arj_version() or "not found: " + ARJ_REPO))


def link(name="memes"):
    """Link the title slide's version to the pushed commit that first has it."""
    source = BUCKETS[name]["source"]
    path = os.path.join(ROOT, source)
    text = open(path, encoding="utf-8", newline="").read()
    v = re.search(r'<span class="deck-version">([^<]*)</span>', text).group(1)
    git = lambda *args: subprocess.run(
        ["git"] + list(args), cwd=ROOT, capture_output=True, text=True
    ).stdout
    commits = git(
        "log",
        "--reverse",
        "--format=%H",
        "-S",
        '<span class="deck-version">%s</span>' % v,
        "--",
        source,
        *BUCKETS[name].get("old", []),
    ).split()
    pushed = [c for c in commits if git("branch", "-r", "--contains", c).strip()]
    if pushed:
        url = GITHUB + "tree/" + quote(pushed[0])
    else:
        url = GITHUB + "commits/master"
        msg = "No pushed commit has version %s yet: it links to the list of commits"
        print(msg % v)

    text, n = re.subn(
        r'<a class="version-link[^"]*"[^>]*>',
        '<a class="version-link ext" href="%s">' % url,
        text,
        count=1,
    )
    open(path, "w", encoding="utf-8", newline="").write(text)
    print(
        "Version",
        v,
        "->",
        url if n else 'no <a class="version-link"> on the title slide',
    )


if __name__ == "__main__":
    if "--link" in sys.argv:
        named = [a for a in sys.argv[1:] if not a.startswith("--")]
        link(named[0] if named else "memes")
    else:
        main(sys.argv[1:])
