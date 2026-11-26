# abrprotowing.com

Static site for ABR Pro Towing (Mississauga, ON), hosted on GitHub Pages.

## Editing
1. Edit business details, service areas, Google reviews, Google posts and photos in `_src/site.json`.
   Page text lives in `_src/build.py`.
2. Regenerate every page, plus `sitemap.xml`, `robots.txt` and `llms.txt`:
   `python3 _src/build.py`
3. Commit and push. GitHub Pages republishes automatically.

Put photos in `img/photos/` as `.webp` or `.jpg`, with descriptive file names and alt text.
`_src/` is never published, because Jekyll skips folders that start with `_`.
