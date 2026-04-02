# Pixera Growth Operator Run

Date: 2026-04-02
Current focus: grow non-brand traffic and improve the visit-to-checkout funnel.

## Current Findings

- The live GA4 stream is correctly set to `G-8233939FQQ`.
- Playwright verification confirmed the live site emits `view_pricing`, `begin_checkout`, `download_installer`, and `generate_lead`.
- GA4 Realtime API returned `1` active user, confirming live ingestion. Historical standard reports are still sparse, which is normal for a newly wired property.
- The biggest SEO bottleneck was page inventory: the site only exposed one indexable landing page.
- The static export hydrates into a React app, so homepage-only HTML edits can be overwritten after load unless they are stabilized in shared runtime code.

## Changes Implemented

- Improved homepage title, description, and structured data to target `mac screenshot editor` and related commercial-intent terms.
- Added `FAQPage` schema to the homepage.
- Added four indexable landing pages targeting high-intent feature keywords:
  - `/mac-screenshot-editor/`
  - `/screenshot-annotation-tool-mac/`
  - `/redact-screenshots-mac/`
  - `/screenshot-backgrounds-mac/`
- Expanded `sitemap.xml` so search engines can discover the new URLs immediately.
- Cleaned up `robots.txt` and refreshed `llm.txt` with the new page inventory.
- Added a homepage guide hub that links the strongest page into the new feature pages and survives hydration on the live site.
- Stabilized runtime metadata on the homepage so the browser title and description no longer revert to stale values after hydration.
- Added `open_guide` event tracking so the new content cluster is measurable in GA4 in addition to the pricing and checkout funnel.

## Keyword Priorities

- Primary:
  - `mac screenshot editor`
  - `screenshot annotation tool mac`
  - `redact screenshots mac`
  - `screenshot backgrounds mac`
- Secondary:
  - `annotate screenshots on mac`
  - `blur screenshot background`
  - `style screenshots for social media`
  - `privacy redaction for screenshots`

## Revenue Tracking Gap

The on-site funnel is now measurable, including guide-page entry (`open_guide`), but purchase confirmation still depends on Lemon Squeezy-side analytics or webhook tracking because checkout completes off-domain.

## Next Actions

1. Finish Search Console verification and submit the expanded sitemap.
2. Add Lemon Squeezy purchase tracking to close the revenue attribution gap.
3. Monitor which of the new landing pages start earning impressions first, then expand the strongest topic cluster with comparison pages and use-case pages.
