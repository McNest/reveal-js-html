"""Commit everything in this repository, on this computer only, named by the
new version and nothing else ("1.8.9").

  python tools/commit.py            version.py --write, then commit
  python tools/commit.py --pdf      version.py --write, rebuild the PDFs
                                    (tools/build_pdf.py), then commit
  python tools/commit.py --no-bump  commit with the version as it is

Never pushes. Before you push you can add to the commit (git add, then
git commit --amend --no-edit), rename it, or undo it and keep the changes
(git reset --soft HEAD~1).
"""

import importlib.util
import os
import subprocess
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TOOLS = os.path.join(ROOT, "tools")


def tool(*args):
    """Run one of this folder's Python tools; stop if it fails"""
    done = subprocess.run([sys.executable, os.path.join(TOOLS, args[0])] + list(args[1:]), cwd=ROOT, check=False)
    if done.returncode:
        sys.exit("%s failed: nothing committed" % args[0])


def git(*args):
    """Run git in this repository"""
    return subprocess.run(["git"] + list(args), cwd=ROOT, check=False)


def written():
    """The version tools/version.py has written"""
    spec = importlib.util.spec_from_file_location("version", os.path.join(TOOLS, "version.py"))
    version = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(version)
    return version.written()


def main(args):
    """Main method"""
    if "--no-bump" not in args:
        tool("version.py", "--write")
    if "--pdf" in args:
        tool("build_pdf.py")
    v = written()
    git("add", "-A")
    if not git("diff", "--cached", "--quiet").returncode:
        sys.exit("Nothing to commit")
    if git("commit", "-m", v).returncode:
        sys.exit("git commit failed")
    print("Committed %s on this computer; not pushed" % v)


if __name__ == "__main__":
    main(sys.argv[1:])
