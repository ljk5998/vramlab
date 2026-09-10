# VRAM Lab

Local AI experiments on the hardware at hand: file paths, memory, compatibility,
and reproducible results. The site uses Hugo, the custom VRAM Lab theme
(`themes/LabDraft`), selected resources from the pinned PaperMod submodule, and
GitHub Pages. React is not used.

## Canonical source and deployment

- Repository: <https://github.com/ljk5998/vramlab>
- Live site: <https://vramlab.com/>
- Active local checkout: the `vramlab-main` directory.
- Deployment branch: `main`; GitHub Actions builds the published site from committed source.
- Experiment designs, private raw logs, and review records live separately in the sibling `vramlab_memory_backup-main/experiments` directory.

The older `vramlab-publish-20260824` directory and memory backups are historical material, not parallel publishing checkouts. Before editing or publishing, verify this checkout's remote, branch, and working tree:

```bash
git remote -v
git status --short --branch
git log -1 --oneline
git fetch origin
git log --oneline HEAD..origin/main
```

Preserve unrelated changes and stage reviewed paths explicitly. Do not upload a local `public/` preview: it can contain drafts or localhost URLs. The Pages workflow produces a fresh production build.

## Local setup and preview

Use Hugo **0.164.0 extended**, matching `.github/workflows/hugo.yaml`, and initialize the pinned theme:

```bash
git submodule update --init --recursive
hugo version
hugo server -D
```

The preview is at `http://localhost:1313/`. `-D` includes drafts; a production build does not.

The approved redesign is enabled by the normal build and Pages workflow.
For a visibly marked, non-indexable review preview, run
`hugo server --config hugo.yaml,hugo.draft.yaml`. See
[Design study 01](design/README.md) and the
[production promotion record](design/PRODUCTION.md) for scope and validation.

```bash
hugo --minify --baseURL "https://vramlab.com/"
```

## New reports

Read `WRITING_STYLE.md` before designing an experiment or writing a report.

```bash
hugo new content posts/my-post-slug.md
```

Keep the new report as a draft during measurement and review. Freeze the experiment inputs, retain failed attempts, compare claims with raw evidence, and execute reader-facing commands in a fresh test environment. Publish only sanitized logs and assets under `static/`.

The filename normally determines the URL. Where an existing report has an explicit `slug`, preserve that published URL. URL changes require a redirect through `aliases`.

For publication, run the content checks and production build, inspect desktop/mobile rendering, verify links and public artifacts, then commit only the reviewed files and push `main`. Confirm both Checks and the Pages deployment, followed by the live article, log, feed, and sitemap.

## Navigation and search policy

- `/start-here/` routes readers by symptom.
- `/fixes/` curates storage, cache, and environment recovery reports.
- `/compatibility/` distinguishes device detection, completed operations, and backend selection.
- `/benchmarks/` explains what each published measurement covers.
- `/posts/` remains the chronological archive; the homepage list and RSS feed contain posts only.
- `/search/` remains available for readers but has `noindex, follow` and is excluded from the sitemap.
- Generated tag/category archives, including empty categories, use the same noindex/sitemap policy through the site cascade. They are not blocked in `robots.txt`.

Curated pages and reports remain indexable. Add a new report to the relevant hub after its URL and content are final. A planned tool does not receive a navigation entry until it exists.

## Project layout

```text
hugo.yaml                         Site settings, homepage, navigation, SEO cascade
content/posts/                    Experiment reports
content/start-here.md              Symptom-based reading route
content/{fixes,compatibility,benchmarks}.md
content/{about,contact,privacy-policy,search}.md
archetypes/posts.md                New report template
themes/LabDraft/                  Active design, local Three.js, generated Archify HTML
hugo.draft.yaml                   Optional non-indexable review mode
assets/css/extended/custom.css    Legacy PaperMod-only styling
layouts/_partials/               Shared SEO/analytics and legacy theme overrides
themes/PaperMod/                   Pinned submodule; do not edit in place
static/logs/                      Sanitized public evidence
.github/workflows/                 Content checks and Pages deployment
static/CNAME                      Custom domain
```

The active theme's `baseof.html` owns head markup, indexing rules and preview
isolation. It reuses shared Open Graph, X cards, structured data, and analytics
partials. The old local `head.html` remains as a PaperMod fallback. The `rss.xml`
override limits the home feed to reports. The structured-data override emits
`BlogPosting` only for reports; navigation and information pages retain
breadcrumbs. Compare shared partials when updating PaperMod.

The current site and Datasets report social cards are generated by `scripts/generate_social_cards.py` using Pillow and Segoe UI/Consolas fonts. The PNG outputs are committed, so building the site does not require Pillow or those fonts. Older report cards remain unchanged.

## Hosting

GitHub repository settings must use **Pages → Build and deployment → GitHub Actions**, with custom domain `vramlab.com` and HTTPS enabled. The existing Cloudflare DNS points the apex to GitHub Pages and `www` to the GitHub Pages host. Hosting configuration is separate from article publication.
