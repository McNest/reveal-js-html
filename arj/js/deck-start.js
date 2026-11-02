/*********************************************************
 * ARJ, Apocalypse Reveal-js: https://github.com/SDevTutors/apocalypse-reveal-js
 * The scripts in this folder sit on top of reveal.js ("all will be
 * revealed"). Version: year.tenth.day, where the year counts from
 * 2026 = 1, the tenth is which tenth of the year (0 to 9), and the day
 * counts the days with changes in that tenth. Set by tools/version.py;
 * shown wherever a slide has <span data-arj-version>.
 *
 * Starts a reveal.js deck, then loads the deck's own scripts in order.
 *
 *   <script src="arj/js/deck-start.js"></script>
 *   <script>
 *     startDeck({
 *       width: 1280, height: 720, ...       // any reveal.js setting
 *       plugins: [RevealMarkdown, RevealNotes],
 *       deckScripts: [                        // loaded one after another,
 *         'deck-markdown.js',                 // once the slides exist
 *         'deck-controls.js',
 *         'deck.js',
 *         'deck-draw.js',
 *       ],
 *     });
 *   </script>
 *
 * A script named without a folder ('deck.js') is loaded from the folder
 * this file came from, so a deck that loads deck-start.js from the hosted
 * copy gets the rest from there too. A path with a folder ('src/js/my.js')
 * or a full address is loaded as it is.
 *
 * Drawing: tldreveal (https://github.com/arthurrump/tldreveal), drawing
 * and notes on the slides with tldraw, is part of ARJ. startDeck loads
 * it from the address in ARJ.tldreveal and adds it to the plugins before
 * reveal.js starts; deck-draw.js then puts its button beside the others.
 * Settings in startDeck:
 *   draw: true,                  // false: no drawing in this deck, no button
 *   drawOnDoubleClick: false,    // true: a double click opens drawing too
 *                                // (tldreveal's own way); false keeps a double
 *                                // click for selecting a word
 *   drawToolbar: 'top',          // tldraw's tools at the 'top' or 'bottom'
 *   tldreveal: { isDarkMode: false, ... }   // tldreveal's own settings
 * Not loaded for the print version (?print-pdf) or the scroll view,
 * which tldreveal does not support. If it can't be loaded (offline), the
 * deck starts without it and shows no drawing button.
 *
 * It also:
 *   - notes the address (#/contents) before reveal.js reads it, as some
 *     slides are only added later (deck-controls.js reads it back)
 *   - explains what to do when a deck that loads a Markdown file is
 *     opened straight from disk, where browsers block the file
 * Returns a promise that resolves once every script has loaded, when it
 * also fires a deck:ready event on the document.
 *********************************************************/
(function () {
	'use strict';

	// The folder deck-start.js was loaded from (arj/js/), and the arj folder
	const here = document.currentScript ? document.currentScript.src.replace(/[^/]*$/, '') : '';

	window.ARJ = {
		name: 'ARJ',
		longName: 'Apocalypse Reveal-js',
		version: '1.8.6', date: '2026-11-02',
		repository: 'https://github.com/SDevTutors/apocalypse-reveal-js',
		// tldreveal's own bundle, React and tldraw included; pinned to a version
		tldreveal: {
			script: 'https://cdn.jsdelivr.net/npm/tldreveal@1.2.0/dist/bundle/index.js',
			style: 'https://cdn.jsdelivr.net/npm/tldreveal@1.2.0/dist/bundle/index.css',
		},
	};
	window.ARJ.folder = here ? new URL('../', here).href : '';
	window.TAP = window.ARJ; // the old name

	function resolve(src) {
		return src.indexOf('/') === -1 ? here + src : src;
	}

	function loadScript(src) {
		return new Promise(function (done, fail) {
			const script = document.createElement('script');
			script.src = src;
			script.onload = done;
			script.onerror = function () { fail(new Error('Could not load ' + src)); };
			document.body.appendChild(script);
		});
	}

	function loadInOrder(sources) {
		return sources.reduce(function (previous, src) {
			return previous.then(function () { return loadScript(resolve(src)); });
		}, Promise.resolve());
	}

	// Opened from disk: a Markdown deck can't fetch its file, so say how to open it
	function explainFileProtocol() {
		const markdown = document.querySelector('.reveal .slides [data-markdown]');
		if (window.location.protocol !== 'file:' || !markdown) return;
		const file = markdown.getAttribute('data-markdown');
		const page = window.location.pathname.split('/').pop();
		document.querySelector('.reveal .slides').innerHTML =
			'<section><h2>Open this through a web server</h2>' +
			'<p>This deck loads <code>' + file + '</code>, and browsers block that from a file.</p>' +
			'<p>In this folder run <code>python -m http.server</code>, then open ' +
			'<code>http://localhost:8000/' + page + '</code>. Or use VS Code Live Server.</p>' +
			'<p>Or read <a href="' + file + '">' + file + '</a> directly.</p></section>';
	}

	function showVersion() {
		document.querySelectorAll('[data-arj-version], [data-tap-version]').forEach(function (el) {
			el.textContent = window.ARJ.version;
			el.title = window.ARJ.name + ' ' + window.ARJ.version + ', ' + window.ARJ.date;
		});
	}

	/* ---------- Drawing (tldreveal) ---------- */
	function drawingWanted(config) {
		if (config.draw === false) return false;
		if (/print-pdf/i.test(window.location.search)) return false;
		if (config.view === 'scroll') return false;
		return true;
	}

	// tldreveal starts drawing on any double click. ARJ opens drawing from its
	// button (or the D key) instead, so a double click can still select a word
	// (drawOnDoubleClick: false, the default). Added before tldreveal's own
	// listener, so it runs first; deck-draw.js also closes drawing if a
	// double click opens it anyway.
	function keepDoubleClick() {
		window.addEventListener('dblclick', function (event) {
			if (!event.target.closest || !event.target.closest('.tldreveal')) event.stopImmediatePropagation();
		}, true);
	}

	function addDrawing(config) {
		if (!drawingWanted(config)) return Promise.resolve();
		const link = document.createElement('link');
		link.rel = 'stylesheet';
		link.href = window.ARJ.tldreveal.style;
		document.head.appendChild(link);
		return loadScript(window.ARJ.tldreveal.script).then(function () {
			if (config.drawOnDoubleClick !== true) keepDoubleClick();
			config.plugins = (config.plugins || []).concat([window.Tldreveal.Tldreveal()]);
			config.tldreveal = Object.assign({ isDarkMode: false }, config.tldreveal || {});
		}, function (error) {
			console.warn('ARJ: drawing is off.', error.message);
		});
	}

	window.startDeck = function (config) {
		explainFileProtocol();
		showVersion();
		document.addEventListener('deck:ready', showVersion); // and in slides added since
		window.deckStartHash = window.location.hash;
		const scripts = config.deckScripts || [];
		return addDrawing(config)
			.then(function () { return Reveal.initialize(config); })
			.then(function () { return loadInOrder(scripts); })
			.then(function () { document.dispatchEvent(new CustomEvent('deck:ready')); });
	};
})();
