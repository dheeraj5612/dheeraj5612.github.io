# Personal website

Static portfolio for [dheerajnamburu.com](https://dheerajnamburu.com/), published by GitHub Pages from the root of `main`. There is no build step and no framework: hand-written HTML and CSS plus one small script.

The first screen shows availability, name, role, a short introduction, contact buttons, four proof numbers, and a career strip. Engineering work, product previews, the product gallery, more projects (the utility portfolio and Daily Cynthia), earlier experience, skills, and contact follow.

The selected logo and favicon use a clipped corner D in navy, white, and blue, chosen after reviewing twenty concepts at 16 and 32 pixels. SVG, ICO, and Apple touch icon variants are in `assets/brand/`.

Phones show a short career summary, three work highlights, and a two column product grid with a full width FilmyCam row, in place of the longer introduction, career strip, and project text. Body text is 16px and nothing is smaller than 12px. Full career history and engineering detail remain below the first screen. Project cards reveal in a short staggered animation with gentle image settling; reduced motion disables these effects.

## Pages

- `index.html`: homepage.
- `utilities/index.html`: directory of the 50 utility sites, 33 live on their own domains and 17 previews, grouped into six categories. Generated, see "Utility directory".
- `404.html`: not found page that GitHub Pages serves for unknown paths. It uses absolute URLs and is marked noindex.
- `filmycam/index.html`: redirect to the FilmyCam App Store listing.
- `robots.txt` and `sitemap.xml`: the sitemap lists `/` and `/utilities/`.

## Styles

- `styles.css`: design tokens as custom properties on `:root`, shared components (header, buttons, section heads, contact panel, footer, analytics consent bar and privacy dialog), and the homepage layout. Mobile first, breakpoints at 380px, 720px and 1080px.
- `utilities/utilities.css`: layout for the directory page only. It loads after `styles.css` and reuses its tokens.
- `styles.css` opens with two fallback `@font-face` rules (`DM Sans Fallback`, `Instrument Serif Fallback`) that scale Arial and Times New Roman to the web font metrics, so text holds its place while the fonts load. Re-measure the overrides if a font file changes.
- When `styles.css` or `analytics.js` changes, bump the `?v=` value on its tag in `index.html` and `404.html`, then regenerate the directory page (it copies the stylesheet link from the homepage). The `utilities.css` version is set inside `tools/gen_utilities.py`.

## Utility directory

`utilities/index.html` is generated. Do not edit it by hand.

Data is in `tools/utilities.json`, one record per site with `slug`, `name`, `url`, `domain`, `what` (one line description), `category`, `status` (`live` or `preview`) and `indexable`. Each live site needs a 640x400 WebP screenshot at `assets/utilities/<slug>.webp` and a 320x200 copy at `assets/utilities/<slug>-320.webp`.

```
python3 tools/gen_utilities.py .
```

The script copies the header, contact section, footer and consent markup from `index.html`, so run it again after changing those. It stops with an error if a thumbnail is missing, a category is unknown, or the totals are not 50 sites, 33 live and 17 previews. Those numbers also appear in the page copy inside the script, so update both together.

## Local preview

Run `python3 -m http.server 4198 --bind 127.0.0.1` from this directory.

## Analytics

Google Analytics property: `558444854`. Web measurement ID: `G-P2LV2GRM83`. [Open the dashboard](https://analytics.google.com/analytics/web/#/a407854991p558444854/reports/intelligenthome).

Tracking starts only after visitors allow analytics. Advertising features are disabled. The footer lets visitors change their choice. Localhost does not send analytics.

Custom events: `contact_email_click`, `resume_download`, `project_visit`, `social_profile_click`, `utility_visit`, `game_visit`, `utilities_directory_click`, `reading_depth`, and `engaged_reading`. `utility_visit` records the site and whether it is live or a preview, `game_visit` covers Daily Cynthia, and `utilities_directory_click` covers homepage links to the directory. Google Analytics adds traffic sources, device information, approximate region, and engagement reports. These data do not identify anonymous visitors by name.

## Assets and dependencies

No CSS framework or other third party code is bundled. DM Sans and Instrument Serif are self hosted with their OFL licenses. DM Sans is trimmed to the 400 to 700 weight range. Product previews show actual app screens: CommandGate in demo state, Fouro's public guest interface, and FilmyCam's App Store imagery. Full resolution versions are retained for the gallery, with smaller WebP copies offered through `srcset`. Where an image fills a box with `object-fit: cover`, its `sizes` value has to cover the larger of the box width and the box height times the image ratio, so re-measure `sizes` when the card layout changes. `assets/utilities/` holds one screenshot thumbnail per live utility site in two widths. `assets/share/og-home-v1.png` is the 1200x630 image used for link previews.

## Publishing

Verify layout, local asset links, consent behavior, and JavaScript syntax before pushing to `main`. Wait for the GitHub Pages build to finish, then check the live HTML, stylesheet, image assets, resume, `/utilities/`, and analytics event delivery.
