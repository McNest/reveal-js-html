/*********************************************************
 * Link icons: each website's own icon (favicon) beside links to it, so
 * "IMDb" or "Wikiquote" can be seen at a glance. Load after the slides
 * exist and after arj/js/deck-markdown.js (the 'label' style uses its
 * field classes), before arj/js/deck-controls.js. Styles in arj/css/arj.css,
 * keyed on data-links on each horizontal slide:
 *   favicon-before   icon, then the link
 *   favicon-after    the link, then the icon
 *   link-icon        the link, then a plain link icon
 *   favicon-label    the icon in place of a field label ("**IMDb:**")
 * ARJ has icons for reveal.js and GitHub only, in arj/img/favicons/. Any
 * other site's icon belongs to the deck that links to it: the deck keeps
 * the icon in its own folder and names the site in sites.
 * Settings, all optional:
 *   linkIcons: {
 *     folder: 'src/img/favicons/',  // where the deck's own icons are (sites)
 *     style: 'favicon-before',      // one of the four, or 'compare': a
 *                                   // different style on each section in turn
 *     sites: { 'imdb.com': ['imdb.png', 'IMDb'], ... },  // the deck's sites,
 *                                   // icons in folder; added to ARJ's two
 *     labels: { 'imdb': 'imdb.com', ... },  // field label -> site, for favicon-label
 *     skip: 'a.person, .no-link-icon',      // links that never get an icon
 *     newTab: false,                // true: links to other websites open in a
 *                                   // new tab, so the deck stays open
 *   }
 * Links that open a new tab (target="_blank", or all of them with newTab)
 * get class opens-tab: an arrow out of a box after the link (arj.css).
 * ?links=favicon-after in the address shows one style everywhere.
 * Links to sites with no icon get a plain link icon. Links that are
 * pictures (a QR code), links matching skip, and links inside an element
 * with class no-link-icon (a title slide that draws its own), get nothing.
 *********************************************************/
(function () {
	'use strict';

	const STYLES = ['favicon-before', 'favicon-after', 'link-icon', 'favicon-label'];

	// ARJ's own: every deck made with it links to these two
	const ARJ_SITES = {
		'revealjs.com': ['revealjs.svg', 'reveal.js'],
		'github.com': ['github.svg', 'GitHub'],
	};

	const PLAIN_LINK = "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%233b5a8c' stroke-width='2.6' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71'/%3E%3Cpath d='M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71'/%3E%3C/svg%3E\")";

	const config = Reveal.getConfig().linkIcons || {};
	const arjFolder = (window.ARJ && window.ARJ.folder ? window.ARJ.folder : 'arj/') + 'img/favicons/';

	// Each site: [the icon's full address, the site's name]
	function inFolder(sites, folder) {
		const out = {};
		Object.keys(sites).forEach(function (domain) {
			out[domain] = [new URL(folder + sites[domain][0], document.baseURI).href, sites[domain][1]];
		});
		return out;
	}

	const settings = {
		style: config.style || 'favicon-before',
		sites: Object.assign(inFolder(ARJ_SITES, arjFolder), inFolder(config.sites || {}, config.folder || '')),
		labels: config.labels || {},
		skip: config.skip || 'a.person, .no-link-icon',
		newTab: config.newTab === true,
	};
	const forced = new URLSearchParams(window.location.search).get('links');

	function siteOf(href) {
		let host = '';
		try { host = new URL(href).hostname.replace(/^www\./, ''); } catch (e) { return null; }
		const key = Object.keys(settings.sites).find(k => host === k || host.endsWith('.' + k));
		return key ? settings.sites[key] : null;
	}

	// 'compare' starts with the first style on the slide after the title
	function styleFor(section) {
		if (STYLES.indexOf(forced) >= 0) return forced;
		if (settings.style !== 'compare') return settings.style;
		return STYLES[(section - 1 + STYLES.length) % STYLES.length];
	}

	// The icon in place of a field label: "**IMDb:**" -> [IMDb icon]:
	function replaceLabels(top) {
		top.querySelectorAll('li.field').forEach(function (item) {
			const name = Array.from(item.classList).find(c => c.indexOf('field-') === 0 && c !== 'field');
			const domain = name && settings.labels[name.slice(6)];
			const label = item.querySelector(':scope > strong:first-child');
			if (!domain || !label || !settings.sites[domain]) return;
			const site = settings.sites[domain];
			const icon = document.createElement('img');
			icon.className = 'label-favicon';
			icon.src = site[0];
			icon.alt = site[1];
			icon.title = site[1];
			label.replaceChildren(icon, ':');
			item.querySelectorAll('a.site-link').forEach(link => link.classList.add('labelled'));
		});
	}

	document.querySelectorAll('.reveal .slides > section').forEach(function (top, h) {
		const style = styleFor(h);
		top.dataset.links = style;
		top.querySelectorAll('a[href]').forEach(function (link) {
			const other = /^https?:/.test(link.href) && new URL(link.href).origin !== window.location.origin;
			if (settings.newTab && other && !link.target) {
				link.target = '_blank';
				link.rel = 'noopener';
			}
			if (link.target === '_blank' && !link.closest('.no-link-icon') && !link.querySelector('img')) link.classList.add('opens-tab');
		});
		top.querySelectorAll('a[href^="http"]:not(:has(img))').forEach(function (link) {
			if (link.matches(settings.skip) || link.closest('.no-link-icon')) return;
			const site = siteOf(link.href);
			link.classList.add('site-link');
			// An absolute address: a relative one in a CSS variable is read from the CSS file
			link.style.setProperty('--favicon', site ? 'url("' + site[0] + '")' : PLAIN_LINK);
		});
		if (style === 'favicon-label') replaceLabels(top);
	});
})();
