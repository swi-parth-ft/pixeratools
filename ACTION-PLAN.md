# Pixera Action Plan

Date: 2026-04-10

## Now

1. Deploy the new Snagit comparison batch:
   - `/pixera-vs-snagit/`
   - homepage guide hub expansion to nine cards
   - descriptive internal-link anchor cleanup across the guide/comparison cluster
2. Keep the descriptive page-title anchor pattern in place. Do not drift back to vague `See the ...` CTA copy on public SEO pages.
3. Preserve the updated crawl inventory files so the new comparison page stays visible to search and AI crawlers immediately.

## Next

1. Restore GA4 and Search Console OAuth scopes, or add a service-account/API path for future automation runs.
2. After deploy, check whether the documentation-heavy comparison branch shows earlier demand than the styling-first branch:
   - Snagit comparison
   - CleanShot X comparison
   - Shottr comparison
3. Add Lemon Squeezy purchase attribution if an API or webhook destination becomes available.

## Later

1. If the Snagit branch earns impressions first, expand it with a sibling buyer-entry page instead of another broad generic landing page.
2. Rerun the deeper audit against the live domain after deployment to replace the localhost-only score with production evidence.
3. If measurement access stays blocked, approve a prompt upgrade that logs the repeated scope error once per run and spends the saved time on content and internal-link work instead.
