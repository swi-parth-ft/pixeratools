# Pixera Deep SEO Audit

Date: 2026-04-03
Scope: local post-fix audit for the static site served from `http://127.0.0.1:4173`
HTML dashboard: `reports/seo/SEO-REPORT.html`
Overall score: `73/100`

## What The Deep Audit Confirmed

- The highest-confidence issues before this pass were crawl readiness and link semantics, not missing landing pages.
- `robots.txt` is now explicit for the AI crawlers that mattered in the pre-fix audit.
- `llms.txt` is now present and high quality, with `llms-full.txt` available for richer context.
- The homepage and guide cluster no longer produce empty-anchor issues in the internal-link crawl.
- Generic repeated `Open guide` anchors have been replaced with workflow-specific link text.

## Evidence

- `robots_checker.py http://127.0.0.1:4173`:
  - all 11 targeted AI crawlers explicitly allowed
- `llms_txt_checker.py http://127.0.0.1:4173`:
  - `llms.txt` found
  - `llms-full.txt` found
  - quality score `95/100`
- `internal_links.py http://127.0.0.1:4173 --depth 1 --max-pages 20 --json`:
  - `issues: []`
  - homepage and guide pages still form a tight 5-to-6-link cluster
- `broken_links.py http://127.0.0.1:4173`:
  - `0` broken
  - `1` redirect
- `social_meta.py http://127.0.0.1:4173`:
  - `92/100`
  - only optional social improvements remain

## Remaining Gaps

- PageSpeed in the local deep report still fails, which is expected for a localhost audit and should not be treated as a confirmed production issue.
- Homepage social tags still lack optional `og:locale` and `og:image` dimension metadata.
- Purchase attribution still depends on Lemon Squeezy-side analytics because checkout completes off-domain.

## Recommended Next Bets

1. Deploy and rerun the deep audit against `https://pixeratools.com` to capture post-deploy live evidence.
2. Wire Lemon Squeezy purchase events into the same GA4 property to close the revenue gap.
3. Expand the guide cluster only after Search Console shows which guide is earning impressions and CTR first.
