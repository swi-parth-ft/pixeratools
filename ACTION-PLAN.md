# Pixera Action Plan

Date: 2026-04-08

## Now

1. Deploy the new page batch:
   - `/documentation-screenshots-mac/`
   - `/pixera-vs-cleanshot-x/`
   - `/pixera-vs-xnapper/`
2. Keep the `FAQPage` schema removal in place. Do not re-add it to this commercial site.
3. Preserve the updated homepage guide hub and internal links so the new pages inherit homepage traffic immediately.

## Next

1. Restore GA4 and Search Console OAuth scopes, or add a service-account/API path for future automation runs.
2. After deploy, check which page gets impressions first:
   - docs use case
   - CleanShot X comparison
   - Xnapper comparison
3. Add Lemon Squeezy purchase attribution if an API or webhook destination becomes available.

## Later

1. Expand the first buyer-entry page that shows impressions into a sibling page instead of publishing another broad landing page.
2. Optionally add `og:locale` across the site for completeness.
3. Rerun the deep audit against the live domain after deployment to replace the localhost-only score with production evidence.
