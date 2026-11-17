# How we make slides

The rules every deck follows. The [meme bank](docs/memes/) is the model: copy its parts rather than inventing new ones. Each deck keeps **its own colours** (the meme bank is light, the CA1 deck is dark blue and green); the parts and the rules below stay the same.

## Files

- Slides are written in Markdown (`deck.md` or similar); `index.html` only loads them. Edit the Markdown.
- `---` with a blank line each side starts the next slide across; `---<!--L2-->` starts a slide underneath (down).
- Diagrams are **Mermaid code in the slide**, drawn in the browser. Never a PNG of a diagram. Do not put `---` front matter in a Mermaid block (it splits the slide); set Mermaid options in the deck's script.
- Every slide has an id: `<!-- .slide: id="failure" -->`. Links between slides use it (`#/figures`), never a slide number.
- Numbering is multilevel, as in the meme bank (`numberFormat: 'multilevel'`): across 4, 5, 6; a slide underneath is 4.1. Its eyebrow shows the same number (`04.1 · Elasticity`). Title, about, finish and the end slides are not numbered (`<!-- no-number -->`).
- Charts: Mermaid first, then interactive JavaScript charts, Python images last. Interactive charts use **Apache ECharts** (SVG renderer) from a small JSON file made by a Python script from the measured data; a Jupyter notebook loads the data and makes the charts by calling those scripts. Python file names have no `-`.

## Title slide

Every title slide has, as in the meme bank:

1. Title and subtitle
2. Author, with the round logo, linked to the author's page
3. Calendar icon and date: the date links to that version (its commit or release)
4. A short quote or line saying what the deck is for
5. "Built with" line: Reveal.js, ARJ, anything else used (Mermaid), and the source, each with its icon
6. QR code to the deck's web address (the GitHub Pages copy of the slides), with the round logo in the middle. Check it scans before use
7. Footer: PDF download, © year and name, version, and the deck's web address

## About slide

The slide after the title, **not numbered**: name and logo, qualifications, GitHub address, email (written reversed in the HTML so it is not harvested, as in the meme bank).

## Words

- Short and plain. Say what was done: "Changed between tests: the number of Product instances", not "I change Product capacity".
- Spell out abbreviations the first time: Application Load Balancer (ALB).
- Explain every measure the first time it appears (for example p95: 95% of requests finished faster than this time).
- Units in full on charts and tables: "Requests per second", not "Requests/s" or "req/s".

## Pictures, charts and captions

- **No title inside a chart image.** The caption is text under the picture, never part of it.
- Every caption starts with a picture icon and its number, linked to the Figures slide: `<a class="ref media" href="#/figures"><sup>2</sup></a> – caption`.
- Pictures as large as the slide allows: the caption and any bullets must still fit. Two or three short bullets go **under** the picture, not in boxes floating beside it.
- Draw charts for slides wide and in the deck's colours (dark deck: dark chart); larger text than the report version.
- A timeline of events is a Mermaid `timeline` diagram, not a row of text and not a squashed gantt. A colon inside a time breaks it: write times with "∶" (U+2236), as in `18∶59∶20`.
- Interactive charts: one chart per measure, side by side or stacked on one time axis (never two measures on one axis). Each panel names its measure above it and has its own small legend. Events are dashed lines. The chart draws itself from the left each time its slide is shown; hover shows values; zoom and save icons at the top right. In the PDF (`?print-pdf`) and the video (`?video`) the icons are hidden and the chart is drawn finished.
- A picture or diagram on the left with a short list on the right is fine (`.two`); each list item and each answer card gets an icon.

## References and links

- A fact from a source gets a reference marker: `<a class="ref" href="#/references"><sup>4</sup></a>` (link icon, then the number).
- Links show their site's icon (link-icons.js); file links show their file type (PDF, Markdown, Python, JSON, notebook), and a folder link shows a folder icon. A link that opens a new page has the external-link icon.
- **File names are links, never code font**: `[report.md](...)`, not `` `report.md` ``. In a deck that will be published, a file link goes to the file on GitHub (`blob/master/...`, folders `tree/master/...`).
- The Figures slide lists each picture and links to **the slide it is on** (`#/elasticity`), so the viewer stays in the deck. Say what it is ("Elasticity timeline"), not how it was drawn.
- Never two icons on one link: if link-icons.js adds one, do not add another by hand.

## End of the deck

In this order, as in the meme bank:

1. **Finish slide** (not numbered): "Questions? Email me" with the email, and a link to the report or handout.
2. Underneath it: **References** (numbered, two columns, each opens its web page), **Figures** (numbered, each opens its slide), **Software used**, and **Links** (source, notes, copyright and any use of generative AI).
3. **Exit slide** ("That's all, folks!") with the exit button, centred.

## PDF and video

- Every deck can be downloaded as a PDF: the title slide's footer links to it (`src/pdf/<deck>.pdf`). Make it with a script that prints `?print-pdf` in a headless browser, so it can be rebuilt after each change; check that charts and diagrams appear in it.
- A screencast is built from the deck, not filmed: one voice recording per slide, and a short face clip (in a circle the size of the logo) only on the title, about and finish slides. A JSON file says which recording goes with which slide; a Python script photographs the slides (`?video` hides buttons and chart icons), films chart slides while they draw, then holds the last frame, and joins it all with ffmpeg. See the CA1 deck's `recording/readme.md`.

## Version and checks

- Version: year.tenth.change (November 2026 is 1.8.x). One more change, one more version; update it on the title slide and in `index.html`.
- Before sharing: open every slide at 1280 × 720, no console errors, nothing runs off the bottom, notes attached, QR code scans, every link and slide link works.

## Learned on the CA1 deck (November 10, 2026)

- **Leaving the slides opens a new tab.** Any link that is not to another slide opens in a new tab with the new-tab arrow after it: websites (`linkIcons: { newTab: true }`) and files beside the deck (`report.md`, `slides.md`, a `.py` or `.json`, a folder). Only `#/slide-id` links stay in the tab.
- **Icons belong to the style, not the HTML.** A slide names an icon with a class (`<span class="arj-icon icon-tus">`, `<h3 class="ic-server">`, `<li class="ic-laptop">`) and only the CSS holds the picture's path. Link icons come from the address (`a[href*="spring.io"]::before`), file icons from the extension.
- **Cards:** number, word, then the icon, on one line (`1 Baseline [icon]`), centred, in the accent colour, with a line under it. Card text with several lines is justified, without hyphenation.
- **References and figures** carry `data-n="4"` / `data-m="2"` on their list items: hovering a marker shows the entry, clicking jumps to it with a "Back to slide" button (ARJ deck.js).
- **Short link** (TinyURL) once, bottom left under the footer line, small, with the TinyURL icon, exactly where ARJ puts it (as in the memes deck): no indent. Its hover is big, with `tinyurl.com/` small and the code large (`data-tip-size="72"`): the code is the only part students need to remember. The QR code itself opens the deck online (its github.io address), not the short link.
- **PDF file name** in kebab case with the author and year (`cloud-scalability-resilience-mark-crowe-2026.pdf`), the same name in `download=""`, and a PDF title set before printing.
- **Timelines** use Mermaid `section`s for the stretches of time, colours that mean something (red errors, amber waiting, blue starting, green healthy) and an emoji on each event. Clock times always `HH:MM:SS`; durations always minutes and seconds as `4m19s`, `1m31s`, `30s`, never `4:19` (it reads as a clock time) and never "4 min 19 s" on one slide and "30 s" on the next. Inside a Mermaid timeline write the colon as `∶` (U+2236): a plain `:` splits the event. The deck lays the rows out again (deck.js `trimTimeline`): every box in a row the same height, text centred, rows close together, the picture as wide as the slide. Stages and times bold, events plain, font 20px. Box widths are not proportional to time: Mermaid draws every event the same width.
- **Hover tips** are dark with light text in a dark deck. Check every kind (a name, a short link, a reference, the bars under a heading): ARJ draws them in `--navy`, which a dark deck may have made light.
- **Data sets:** under every chart and timeline caption, on its own line, "Data: name.csv" (`<p class="fig-data">`, `a.data-link`). It does not download: it goes to the **Data sets** slide at the end, marks that row and offers "Back to slide n". That slide has, for each data set, its figure, rows, **View** (a Markdown copy on github.com, which shows it as a table with what each column means; made from the CSV by a Python script) and the CSV to download. Facts about a table ("at 200 users") go in the table's header, not the figure caption.
- **Terms the audience may not know** (p95) get a reference to where the name comes from (AWS CloudWatch statistics), not only a definition.
- **Only the changes asked for.** Do not move, restyle or reword anything Mark did not ask about; suggest it instead.
- **Title slide:** room above the title. The QR code floats right with the date under it, smaller than the name. Beside it: the question, the description, the name, the module, the course on its own line (the college's icon stands for its name), a film quote. "Built with" goes the full width under the QR code, small: what the deck is about comes first, how it was made last.
- **About the author:** the square logo, the name with the new-tab arrow (it leaves the deck), the tech stack as small tags with their logos, then links and an Education list. No years that give away an age.
- **Software used:** one card per kind (AWS, Applications, Scripts, Load testing, Data and charts, Diagrams and slides, Video), each an icon and heading with its products on one line under it, three columns. A tool is listed under what it is (the AWS CLI is software, not a script).
- **Links to Markdown files** go to github.com (`/blob/master/...md`, with `#heading` for a section), where they are shown formatted; a notebook (`.ipynb`) likewise.
