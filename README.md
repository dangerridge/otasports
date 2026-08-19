# OTA Sports

Static HTML/CSS site for https://otasports.info/

## SEO behavior
- The actual page topic is the single H1; the OTA SPORTS brand is no longer an H1.
- `/sports-on-tv-today/` pages stay indexable every day.
- Empty dated archive pages use `noindex,follow`.
- Empty dated pages are omitted from `sitemap.xml`.
- Dated pages with verified OTA events remain indexable and are included in the sitemap.
- Each market has an `/archive/` page.
- Dated pages have previous/next/archive navigation.
- No cable information or public source/reference sections.

## Deploy
Replace the repository contents with this folder and push to GitHub Pages.
