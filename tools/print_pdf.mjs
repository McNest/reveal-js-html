// Print a reveal.js deck to PDF, the way the browser's Save as PDF does,
// once the deck has finished building its print pages.
//
//   node tools/print_pdf.mjs URL OUT.pdf [width height]
//   node tools/print_pdf.mjs "http://localhost:8008/docs/memes/?print-pdf" docs/memes/src/pdf/memes.pdf
//
// tools/build_pdf.py runs it for every deck, with a server of its own.
//
// Starts Microsoft Edge (or Chrome, with BROWSER=path) headless with the
// DevTools protocol, opens the deck, waits until the number of .pdf-page
// elements stops changing, then calls Page.printToPDF with one slide per
// page (1280 x 720 by default, as in the decks). Needs Node 22+ (WebSocket).
import { spawn } from 'node:child_process';
import { writeFileSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const [url, out, width = '1280', height = '720'] = process.argv.slice(2);
if (!url || !out) {
	console.error('usage: node print_pdf.mjs URL OUT.pdf [width height]');
	process.exit(1);
}
const browser = process.env.BROWSER || 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const port = 9300 + Math.floor(Math.random() * 500);
const profile = mkdtempSync(join(tmpdir(), 'print-pdf-'));
const child = spawn(browser, ['--headless=new', '--disable-gpu', '--remote-debugging-port=' + port,
	'--user-data-dir=' + profile, '--no-first-run', 'about:blank'], { stdio: 'ignore' });

const sleep = ms => new Promise(done => setTimeout(done, ms));

async function target() {
	for (let i = 0; i < 50; i++) {
		try {
			const list = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
			const page = list.find(t => t.type === 'page');
			if (page) return page.webSocketDebuggerUrl;
		} catch { /* not up yet */ }
		await sleep(200);
	}
	throw new Error('the browser did not start');
}

const socket = new WebSocket(await target());
await new Promise(done => socket.addEventListener('open', done));
let id = 0;
const waiting = new Map();
socket.addEventListener('message', event => {
	const message = JSON.parse(event.data);
	if (message.id && waiting.has(message.id)) {
		waiting.get(message.id)(message);
		waiting.delete(message.id);
	}
});
function send(method, params = {}) {
	return new Promise(done => {
		waiting.set(++id, done);
		socket.send(JSON.stringify({ id, method, params }));
	});
}
async function evaluate(expression) {
	const reply = await send('Runtime.evaluate', { expression, returnByValue: true });
	return reply.result && reply.result.result ? reply.result.result.value : undefined;
}

try {
	await send('Page.enable');
	await send('Emulation.setDeviceMetricsOverride', { width: +width, height: +height, deviceScaleFactor: 1, mobile: false });
	await send('Page.navigate', { url });
	let last = -1, steady = 0;
	for (let i = 0; i < 240 && steady < 6; i++) {
		await sleep(500);
		const pages = await evaluate("document.querySelectorAll('.pdf-page').length");
		steady = pages > 0 && pages === last ? steady + 1 : 0;
		last = pages;
	}
	if (last <= 0) throw new Error('no print pages: is ?print-pdf in the address?');
	await sleep(1500); // pictures
	const inch = px => px / 96;
	const reply = await send('Page.printToPDF', {
		printBackground: true, preferCSSPageSize: true,
		paperWidth: inch(+width), paperHeight: inch(+height),
		marginTop: 0, marginBottom: 0, marginLeft: 0, marginRight: 0,
	});
	if (!reply.result) throw new Error(JSON.stringify(reply.error));
	writeFileSync(out, Buffer.from(reply.result.data, 'base64'));
	console.log(out, last, 'slides');
} finally {
	socket.close();
	child.kill();
}
