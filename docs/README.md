# B1/B2 Digital Work Studio — buyer website

An original static service site and client-only CSV/JSON data workbench. It makes **no** claim of customers, earned money, submitted bids or received crypto. No confidential information should be entered in public GitHub requests.

## Publicly deployed temporary preview (independently checked)

**Live site:** https://utopian-femur-oczcu.ship.place/ — anonymous static-host deployment confirmed 18 November 2026; [GitHub deploy run](https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions/runs/44288043215) and [independent external HTTP smoke check](https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions/runs/44288291852) both succeeded. This is a **temporary** free preview, expiring 25 November 2026 at 10:43 UTC. It is public but unlisted/noindex; it is NOT a permanent indexed marketing website. Its published quote form is a public GitHub issue, so buyer must sign into GitHub. No client contract or incoming crypto payment is established by publishing it.

For a durable URL and automatic deployment, enable GitHub Pages in repo Settings > Pages (source main /docs). Do not replace the public preview with an assumed GitHub Pages URL before activation.

## Preview

From repository root: `python -m http.server 8000 --directory docs`. Open `http://localhost:8000`.

## Publish free with GitHub Pages

The site files are in `main/docs`. A repository admin must enable: **Settings → Pages → Build and deployment → Deploy from a branch → main → /docs → Save**. Once activated, visit `https://kwesigaamon8-web.github.io/Amon-Kwesiga/` and test the interactive workbench.

A GitHub commit **does not automatically enable Pages**. The source can also be previewed through the third-party raw.githack proxy; it displays a caution screen before serving HTML and offers no hosting guarantee.

## Browser data tool

No runtime package or backend. Input never leaves the browser. Supports CSV and flat JSON arrays, duplicate-key detection, empty-cell counts, numeric totals, JSON/CSV exports and formula-protected CSV spreadsheet output. Maximum 5 MB, 30,000 records, 100 columns. This is descriptive data QA, **not a formal audit**.

Run tests with `node --test docs/tests/engine.test.js` (Node 18+).

## Work orders and cryptocurrency

The website links to the existing verified owner-controlled GitHub paid-service issue template. Public issues must include **only anonymized samples**. Any actual buyer must agree scope, acceptance checks, deadlines and payment terms. Confirm exact asset/network, wallet control, token issuer/mint and memo requirements before providing one receiving route. Do not use any unverified exchange identifier. No email, wallet signature, transfer or money collection is performed by the public website.
