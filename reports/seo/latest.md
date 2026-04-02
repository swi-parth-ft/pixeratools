# Pixera SEO And Analytics Baseline

Date: 2026-04-02
Current focus: analytics setup, Search Console readiness, and sales funnel tracking.

## Current State

- Homepage metadata now has a canonical URL and stronger sales-oriented copy.
- The site emits `view_pricing`, `begin_checkout`, `download_installer`, and `generate_lead`.
- `robots.txt` and `sitemap.xml` are present for Search Console submission.
- Search Console ownership verification is still pending because it requires account or DNS access.

## Immediate Admin Tasks

1. In GA4, keep `G-8233939FQQ` as the active web stream for `https://pixeratools.com/`.
2. Mark `begin_checkout`, `download_installer`, and `generate_lead` as key events.
3. Add event-scoped custom dimensions for `cta_location`, `item_name`, `platform`, and `link_url`.
4. In Search Console, add the Domain property `pixeratools.com`, verify by DNS TXT, and submit `https://pixeratools.com/sitemap.xml`.
5. Associate Search Console with the GA4 property after verification.

## Important Limitation

Checkout clicks are tracked, but confirmed purchases still need Lemon Squeezy-side tracking or a server-side webhook because checkout completes off-domain.
