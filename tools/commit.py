"""Commit what has changed, on this computer only: one commit for each deck
that changed, and one for everything else ("site"), each named by its new
version and nothing else.

  python tools/commit.py            for each one that changed: version.py
                                    --write, then commit its files alone
  python tools/commit.py --pdf      the same, rebuilding each changed deck's
                                    PDF first (tools/build_pdf.py)
  python tools/commit.py --no-bump  commit with the versions as they are

Which files belong to which deck: tools/version.py (BUCKETS). A commit is
named "memes 1.8.9": the deck, then its version, as the decks count apart.

Never pushes. Before you push you can add to the last commit (git add, then
git commit --amend --no-edit), rename it, or undo it and keep the changes
(git reset --soft HEAD~1).
"""

import importlib.util
import os
import subprocess
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TOOLS = os.path.join(ROOT, "tools")


def load(name):
    """One of this folder's Python tools, as a module"""
    spec = importlib.util.spec_from_file_location(name, os.path.join(TOOLS, name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git(*args, capture=False):
    """Run git in this repository"""
    return subprocess.run(["git"] + list(args), cwd=ROOT, check=False, capture_output=capture, text=True)


def changed():
    """Every changed, new or deleted file, staged or not, from ROOT"""
    out = git("status", "--porcelain", "-z", "--untracked-files=all", capture=True).stdout
    paths, parts = [], out.split("\0")
    i = 0
    while i < len(parts):
        entry = parts[i]
        if len(entry) > 3:
            paths.append(entry[3:])
            if entry[0] in "RC":  # renamed or copied: the old path follows
                i += 1
                paths.append(parts[i])
        i += 1
    return paths


def pathspec(version, name):
    """git's paths for one deck, or for everything that isn't a deck"""
    folder = version.BUCKETS[name]["folder"]
    if folder:
        return [folder]
    return ["."] + [":(exclude)" + b["folder"] for b in version.BUCKETS.values() if b["folder"]]


def main(args):
    """Main method"""
    version = load("version")
    names = []
    for path in changed():
        name = version.bucket_of(path)
        if name not in names:
            names.append(name)
    if not names:
        sys.exit("Nothing to commit")
    decks = load("build_pdf").DECKS
    for name in [n for n in version.BUCKETS if n in names]:  # in BUCKETS order
        v = version.write(name) if "--no-bump" not in args else version.written(name)
        if "--pdf" in args and name in decks:
            if subprocess.run([sys.executable, os.path.join(TOOLS, "build_pdf.py"), name], cwd=ROOT, check=False).returncode:
                sys.exit("The %s PDF failed: %s not committed" % (name, name))
        spec = pathspec(version, name)
        git("add", "-A", "--", *spec)
        message = "%s %s" % (name, v)
        if git("commit", "-m", message, "--", *spec).returncode:
            sys.exit("git commit failed for " + name)
        print("Committed %s on this computer; not pushed" % message)


if __name__ == "__main__":
    main(sys.argv[1:])
