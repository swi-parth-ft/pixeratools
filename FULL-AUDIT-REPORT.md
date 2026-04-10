# Pixera Full Audit Report

Date: 2026-04-10
Audit target: `http://127.0.0.1:4210`
Dashboard: `reports/seo/SEO-REPORT-2026-04-10.html`
Overall score: `72/100`

## Summary

- Crawl files are healthy:
  - `robots.txt` explicitly allows the targeted AI crawlers
  - `llms.txt` and `llms-full.txt` score `100/100`
  - `sitemap.xml` parses cleanly
- Internal discovery is stronger after the Snagit batch:
  - `84` internal links in the local crawl
  - no orphan candidates
  - the new `/pixera-vs-snagit/` page already receives `6` incoming links
- No broken-link regression was introduced:
  - `0` broken links
  - `1` redirect
- Social meta is solid on the homepage and the new comparison page:
  - `100/100` on `http://127.0.0.1:4210`
  - `100/100` on `http://127.0.0.1:4210/pixera-vs-snagit/`

## Confirmed Improvements

1. Added one new buyer-entry page for the documentation-heavy incumbent query:
   - `pixera-vs-snagit`
2. Expanded the homepage guide hub to nine cards so the Snagit page inherits direct homepage visibility.
3. Rewired the guide/comparison cluster away from generic CTA anchor text into descriptive page-title anchors.
4. Updated crawl inventory files (`sitemap.xml`, `llm.txt`, `llms.txt`, `llms-full.txt`) to match the new page set and the pricing-localization guardrail.

## Confirmed Limitations

- GA4 refresh failed with `ACCESS_TOKEN_SCOPE_INSUFFICIENT`.
- Search Console refresh failed with `ACCESS_TOKEN_SCOPE_INSUFFICIENT`.
- Lemon Squeezy purchase data is still unavailable in this workspace.
- `pagespeed.py` failed inside the localhost dashboard run; that is an environment limitation for localhost, not proof of a live production regression.

## Key Takeaway

The structural SEO work is now healthy enough that the next material blocker is not crawl readiness or page inventory. The real bottleneck is still measurement access. Until GA4 and GSC scopes are fixed, the best use of the automation is to keep shipping high-intent pages and stronger internal-link routing without pretending live movement is known.
