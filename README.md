# OTA Sports — corrected 11-market build

This repository generates a plain static HTML/CSS site for https://otasports.info/.

The inclusion rule is **all sports-oriented OTA programming**, not merely live games:
live events, delays, replays, wrestling, sumo, racing, poker, combat sports, sports magazines,
highlights, local sports talk, recaps and other clearly sports-oriented broadcasts.

Cable-only and streaming-only availability is excluded unless there is a verified OTA simulcast.

## Markets
New York, Los Angeles, Chicago, Dallas–Fort Worth, Philadelphia, Houston, Atlanta,
Washington DC, San Francisco Bay Area, Boston, and Toronto.

## Today / Tomorrow rollover
GitHub rebuilds shortly after local midnight:
- Eastern: 12:07 AM
- Central: 12:09 AM
- Pacific: 12:11 AM

Toronto rolls with Eastern Time.

## One-time GitHub Pages setting
Repository → Settings → Pages → Build and deployment → Source → **GitHub Actions**

## Daily update
Add one JSON file per market:
`data/daily/<market-slug>/YYYY-MM-DD.json`

Then push. GitHub rebuilds the dated pages, archive, sitemap, Today and Tomorrow aliases.

## SEO
- one meaningful H1 per page
- canonical URLs
- Today/Tomorrow pages remain indexable
- empty dated pages use `noindex,follow`
- empty dated pages are omitted from sitemap.xml
- dated pages with verified listings are indexable
- public pages contain no source/reference sections or external source links


## Repository layout

The deployable static site is at the repository root (`index.html`, market folders, `robots.txt`, `sitemap.xml`).
The `data/` JSON files and `scripts/` folder are support files used by GitHub Actions to regenerate Today/Tomorrow pages automatically.

You can open the repository and see the actual HTML site immediately; `_site/` is no longer included in this package.
