# Reveal.js

Slide decks by [Mark Crowe](https://sdevtutors.github.io/mark-crowe/), made with [reveal.js](https://revealjs.com/) and [ARJ](https://github.com/SDevTutors/apocalypse-reveal-js) (Apocalypse Reveal-js).

- Online: <https://mcnest.github.io/reveal-js-html/>, a page with a link to each deck

---

| Page                                      | What it is                                                                          |
|-------------------------------------------|-------------------------------------------------------------------------------------|
| [index.html](index.html)                  | The list of decks: start here                                                       |
| [memes/index.html](docs/memes/index.html) | Meme Bank: film and TV quotes for memes. Short link: <https://tinyurl.com/4u26rwnh> |
| [memes.md](docs/memes/memes.md)           | The meme bank as text: every slide in `index.html` comes from this file             |
| [fyp/index.html](docs/fyp/index.html)     | Final Year Projects: the habits nobody teaches you (was `index.html`)               |
| [asg2/index.html](docs/asg2/index.html)   | Training Needs Analysis: purpose, benefits, methods and process                     |

Each deck has an exit button at its top right that goes back to the page before it, or closes the tab if it opened in a tab of its own.

The decks load [ARJ](https://github.com/SDevTutors/apocalypse-reveal-js) from its GitHub Pages site, so a change to ARJ shows in the decks once it is pushed.

## Short links and QR codes

The meme bank has a TinyURL, <https://tinyurl.com/4u26rwnh>, on its title slide, in its QR code (`docs/memes/src/img/qr/memes-deck-tinyurl.svg`) and on [index.html](index.html). TinyURL only forwards to the address it was given: **whenever the deck's address changes** (a renamed repository or folder, a move to another account or organisation), sign in at [tinyurl.com](https://tinyurl.com/) and point the short link at the new address. The QR code holds the short link, so it keeps working once the short link is updated.

| Short link                     | Goes to                                                     |
|--------------------------------|-------------------------------------------------------------|
| <https://tinyurl.com/4u26rwnh> | <https://mcnest.github.io/reveal-js-html/docs/memes/>       |
| <https://tinyurl.com/42m5nncm> | Old: the meme bank's first address (`memes.html`), now gone |

## Tools

Run them from this folder (the repository's); each one's own notes say more.

| Command                          | What it does                                                                                       |
|----------------------------------|----------------------------------------------------------------------------------------------------|
| `python tools/serve.py`          | Serves the decks at <http://localhost:8008/>, for trying a change                                  |
| `python tools/version.py --write`| One more change: the new version and date on the decks' title slides                               |
| `python tools/build_pdf.py`      | Rebuilds each deck's PDF (`docs/*/src/pdf/`) from its print version, with the ARJ clone beside this one if there is one. Needs Node 22+ and Edge or Chrome |
| `python tools/commit.py`         | `version.py --write`, then a commit on this computer named by the version alone ("1.8.9"); `--pdf` rebuilds the PDFs first. Never pushes: amend or undo it first if you like (`git reset --soft HEAD~1`), then push |
