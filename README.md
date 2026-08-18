# otasports.info static site

Plain HTML + CSS. Each page contains a tiny inline Day/Night toggle so nested GitHub Pages paths cannot break the theme control. Listings remain readable and crawlable with JavaScript disabled.

## Changes in this build
- New York linked from homepage.
- Philadelphia and New York daily pages use one overall OTA listing.
- Wrestling, sumo and odd/hidden-gem programming are no longer split into separate daily sections.
- Visible source sections removed from daily pages.
- Day/Night mode added and remembered in localStorage.
- Philadelphia canonicals corrected from example.com to otasports.info.
- WDUM-LD 41.5 Fubo Sports Network given a Philadelphia channel page.
- Existing evergreen wrestling URLs retained so old links do not break.

Deploy the contents of this folder to the repository root.


## Theme

The day/night toggle is now self-contained in each HTML page. It does not depend on an external JavaScript asset; it stores the visitor preference when localStorage is available and still toggles if storage is blocked.

## Editorial rule

Do not list cable-only or streaming-only events. The public pages contain only OTA listings, OTA channels whose exact schedules are pending verification, and scan-coverage notes.
