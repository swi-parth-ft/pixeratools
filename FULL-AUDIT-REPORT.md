# Pixera Full Audit Report

Date: 2026-04-08
Audit target: `http://127.0.0.1:4180`
Dashboard: `reports/seo/SEO-REPORT-2026-04-08.html`
Overall score: `72/100`

## Summary

- Crawl files are healthy:
  - `robots.txt` explicitly allows the targeted AI crawlers
  - `llms.txt` and `llms-full.txt` score `100/100`
  - `sitemap.xml` parses cleanly
- Internal discovery is healthier after this batch:
  - no orphan candidates in the local crawl
  - the new docs and comparison pages already receive 5-8 internal links each
- No broken-link regression was introduced:
  - `0` broken links
  - `1` redirect
- Social meta is solid on the homepage and new pages:
  - `92/100`
  - only optional `og:locale` remains missing

## Confirmed Improvements

1. Added three new buyer-entry pages:
   - documentation use case
   - CleanShot X comparison
   - Xnapper comparison
2. Expanded homepage internal linking so the new pages inherit direct homepage visibility.
3. Removed `FAQPage` JSON-LD from the commercial site while preserving visible FAQ content.
4. Updated crawl inventory files (`sitemap.xml`, `llm.txt`, `llms.txt`, `llms-full.txt`) to match the new page set.

## Confirmed Limitations

- GA4 refresh failed with `ACCESS_TOKEN_SCOPE_INSUFFICIENT`.
- Search Console refresh failed with `ACCESS_TOKEN_SCOPE_INSUFFICIENT`.
- Lemon Squeezy purchase data is still unavailable in this workspace.
- Local `pagespeed.py` failed in the generated HTML report; that is an environment limitation for localhost, not proof of a live production regression.

## Key Takeaway

Pixera now has a stronger content graph and a more defensible schema setup, but the next strategic decision still depends on restoring live analytics access. The page inventory problem is no longer the main blocker.
