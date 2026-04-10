(function () {
  var seen = {};
  var initialized = false;
  var metadataStabilized = false;
  var PAGE_METADATA = {
    "/": {
      title: "Mac Screenshot Editor for Styled Screenshots | Pixera",
      description: "Pixera is a Mac screenshot editor for styling, annotating, and redacting screenshots with gradients, blur backgrounds, shadows, and export-ready layouts.",
      keywords: "mac screenshot editor, screenshot annotation tool mac, redact screenshots mac, screenshot backgrounds mac",
      canonical: "https://pixeratools.com/"
    },
    "/index.html": {
      title: "Mac Screenshot Editor for Styled Screenshots | Pixera",
      description: "Pixera is a Mac screenshot editor for styling, annotating, and redacting screenshots with gradients, blur backgrounds, shadows, and export-ready layouts.",
      keywords: "mac screenshot editor, screenshot annotation tool mac, redact screenshots mac, screenshot backgrounds mac",
      canonical: "https://pixeratools.com/"
    },
    "/mac-screenshot-editor/": {
      title: "Mac Screenshot Editor for Polished Images | Pixera",
      description: "Pixera is a Mac screenshot editor for polished screenshots with gradients, blur backgrounds, annotations, privacy redaction, and export-ready layouts.",
      keywords: "mac screenshot editor, screenshot editor mac, style screenshots mac, annotate screenshots mac, redact screenshots mac",
      canonical: "https://pixeratools.com/mac-screenshot-editor/"
    },
    "/screenshot-annotation-tool-mac/": {
      title: "Screenshot Annotation Tool for Mac | Pixera",
      description: "Use Pixera as a screenshot annotation tool for Mac to add arrows, labels, highlights, and clear product callouts without leaving your screenshot workflow.",
      keywords: "screenshot annotation tool mac, annotate screenshots on mac, screenshot markup tool, arrows on screenshots mac",
      canonical: "https://pixeratools.com/screenshot-annotation-tool-mac/"
    },
    "/redact-screenshots-mac/": {
      title: "Redact Screenshots on Mac Privately | Pixera",
      description: "Redact screenshots on Mac with Pixera before sharing emails, API keys, customer names, and other sensitive details in docs, posts, and support replies.",
      keywords: "redact screenshots mac, redact sensitive info from screenshots, blur private data screenshots, screenshot redaction mac",
      canonical: "https://pixeratools.com/redact-screenshots-mac/"
    },
    "/screenshot-backgrounds-mac/": {
      title: "Beautiful Screenshot Backgrounds on Mac | Pixera",
      description: "Create beautiful screenshot backgrounds on Mac with Pixera using blur, gradients, adaptive insets, and polished framing for social posts, docs, and product marketing.",
      keywords: "screenshot backgrounds mac, blur screenshot background, gradient screenshot backgrounds, style screenshots mac",
      canonical: "https://pixeratools.com/screenshot-backgrounds-mac/"
    },
    "/documentation-screenshots-mac/": {
      title: "Documentation Screenshots for Mac | Pixera",
      description: "Create documentation screenshots on Mac with Pixera using arrows, labels, polished backgrounds, and privacy-safe cleanup for help centers, onboarding guides, and release notes.",
      keywords: "documentation screenshots mac, annotate screenshots for docs, help center screenshots, changelog screenshots",
      canonical: "https://pixeratools.com/documentation-screenshots-mac/"
    },
    "/pixera-vs-cleanshot-x/": {
      title: "Pixera vs CleanShot X for Polished Screenshots",
      description: "Compare Pixera vs CleanShot X for Mac screenshot workflows, including polished styling, annotation, redaction, capture breadth, and straightforward pricing.",
      keywords: "pixera vs cleanshot x, cleanshot x alternative, screenshot app comparison mac",
      canonical: "https://pixeratools.com/pixera-vs-cleanshot-x/"
    },
    "/pixera-vs-shottr/": {
      title: "Pixera vs Shottr for Mac Screenshot Workflows",
      description: "Compare Pixera and Shottr across screenshot styling, annotations, scrolling capture, OCR, pricing, and which Mac workflow fits docs, support, and launches better.",
      keywords: "pixera vs shottr, shottr alternative, mac screenshot app comparison",
      canonical: "https://pixeratools.com/pixera-vs-shottr/"
    },
    "/pixera-vs-snagit/": {
      title: "Pixera vs Snagit for Documentation Screenshots",
      description: "Compare Pixera and Snagit for Mac documentation screenshots, annotation, privacy cleanup, step-guide automation, capture breadth, and buying tradeoffs.",
      keywords: "pixera vs snagit, snagit alternative mac, documentation screenshots tool",
      canonical: "https://pixeratools.com/pixera-vs-snagit/"
    },
    "/pixera-vs-xnapper/": {
      title: "Pixera vs Xnapper for Styled Screenshots",
      description: "Compare Pixera vs Xnapper for Mac screenshot styling, annotations, redaction, pricing, and which workflow fits docs, launches, and polished exports better.",
      keywords: "pixera vs xnapper, xnapper alternative, screenshot beautifier mac",
      canonical: "https://pixeratools.com/pixera-vs-xnapper/"
    }
  };
  var GUIDE_PATHS = {
    "/mac-screenshot-editor/": "mac-screenshot-editor",
    "/screenshot-annotation-tool-mac/": "screenshot-annotation-tool-mac",
    "/redact-screenshots-mac/": "redact-screenshots-mac",
    "/screenshot-backgrounds-mac/": "screenshot-backgrounds-mac",
    "/documentation-screenshots-mac/": "documentation-screenshots-mac",
    "/pixera-vs-cleanshot-x/": "pixera-vs-cleanshot-x",
    "/pixera-vs-shottr/": "pixera-vs-shottr",
    "/pixera-vs-snagit/": "pixera-vs-snagit",
    "/pixera-vs-xnapper/": "pixera-vs-xnapper"
  };
  var RESOURCE_PATHS = {
    "/blog/app-screenshots-for-app-store-2026.html": "app-screenshots-for-app-store-2026",
    "/blog/app-store-screenshot-sizes-2026.html": "app-store-screenshot-sizes-2026"
  };
  var GUIDE_SECTION_HTML = [
    '<section id="guides" aria-label="Pixera screenshot workflow guides" class="bg-white py-20 sm:py-24">',
    '<div class="workflow-guides-shell">',
    '<div class="workflow-guides-intro">',
    '<p class="workflow-guides-kicker">Workflow Guides</p>',
    '<h2 class="workflow-guides-title font-display">Choose the Pixera page that matches your workflow.</h2>',
    '<p class="workflow-guides-copy">Browse the highest-intent Pixera pages: core workflow guides, documentation use cases, and honest comparisons against the Mac screenshot tools buyers already know.</p>',
    '</div>',
    '<div class="workflow-guides-grid">',
    '<a class="workflow-guide-card" href="/mac-screenshot-editor/">',
    '<p class="workflow-guide-label">Core Guide</p>',
    '<h3 class="workflow-guide-title font-display">Mac Screenshot Editor</h3>',
    '<p class="workflow-guide-body">The main Pixera workflow for styling, annotation, privacy cleanup, and export-ready screenshot presentation.</p>',
    '<span class="workflow-guide-cta">Mac Screenshot Editor</span>',
    '</a>',
    '<a class="workflow-guide-card" href="/documentation-screenshots-mac/">',
    '<p class="workflow-guide-label">Use Case</p>',
    '<h3 class="workflow-guide-title font-display">Documentation Screenshots</h3>',
    '<p class="workflow-guide-body">See how Pixera keeps help center, onboarding, and changelog screenshots clearer with annotations, balanced framing, and privacy-safe cleanup.</p>',
    '<span class="workflow-guide-cta">Documentation Screenshots for Mac</span>',
    '</a>',
    '<a class="workflow-guide-card" href="/screenshot-annotation-tool-mac/">',
    '<p class="workflow-guide-label">Use Case</p>',
    '<h3 class="workflow-guide-title font-display">Screenshot Annotation Tool</h3>',
    '<p class="workflow-guide-body">Learn how to add arrows, labels, and clear product callouts without breaking the screenshot workflow.</p>',
    '<span class="workflow-guide-cta">Screenshot Annotation Tool for Mac</span>',
    '</a>',
    '<a class="workflow-guide-card" href="/redact-screenshots-mac/">',
    '<p class="workflow-guide-label">Privacy</p>',
    '<h3 class="workflow-guide-title font-display">Redact Screenshots on Mac</h3>',
    '<p class="workflow-guide-body">See how Pixera protects emails, API keys, customer names, and other sensitive details before sharing screenshots.</p>',
    '<span class="workflow-guide-cta">Redact Screenshots on Mac</span>',
    '</a>',
    '<a class="workflow-guide-card" href="/screenshot-backgrounds-mac/">',
    '<p class="workflow-guide-label">Styling</p>',
    '<h3 class="workflow-guide-title font-display">Screenshot Backgrounds</h3>',
    '<p class="workflow-guide-body">Use blur, gradients, and adaptive insets to make screenshots feel sharper in docs, social posts, and launch pages.</p>',
    '<span class="workflow-guide-cta">Screenshot Backgrounds on Mac</span>',
    '</a>',
    '<a class="workflow-guide-card" href="/pixera-vs-cleanshot-x/">',
    '<p class="workflow-guide-label">Comparison</p>',
    '<h3 class="workflow-guide-title font-display">Pixera vs CleanShot X</h3>',
    '<p class="workflow-guide-body">Compare polished still-image workflows, annotation depth, capture breadth, and pricing before choosing your Mac screenshot tool.</p>',
    '<span class="workflow-guide-cta">Compare Pixera vs CleanShot X</span>',
    '</a>',
    '<a class="workflow-guide-card" href="/pixera-vs-shottr/">',
    '<p class="workflow-guide-label">Comparison</p>',
    '<h3 class="workflow-guide-title font-display">Pixera vs Shottr</h3>',
    '<p class="workflow-guide-body">Compare Pixera with Shottr across backgrounds, annotation tools, scrolling capture, OCR, pricing, and the screenshot jobs each app fits best.</p>',
    '<span class="workflow-guide-cta">Compare Pixera vs Shottr</span>',
    '</a>',
    '<a class="workflow-guide-card" href="/pixera-vs-snagit/">',
    '<p class="workflow-guide-label">Comparison</p>',
    '<h3 class="workflow-guide-title font-display">Pixera vs Snagit</h3>',
    '<p class="workflow-guide-body">Compare Pixera with Snagit across documentation workflows, step-guide automation, smart redaction, broader capture features, and still-image polish.</p>',
    '<span class="workflow-guide-cta">Compare Pixera vs Snagit</span>',
    '</a>',
    '<a class="workflow-guide-card" href="/pixera-vs-xnapper/">',
    '<p class="workflow-guide-label">Comparison</p>',
    '<h3 class="workflow-guide-title font-display">Pixera vs Xnapper</h3>',
    '<p class="workflow-guide-body">Compare Pixera with Xnapper across styling workflow, annotations, redaction, and the kinds of screenshot jobs each app fits best.</p>',
    '<span class="workflow-guide-cta">Compare Pixera vs Xnapper</span>',
    '</a>',
    '</div>',
    '</div>',
    '</section>'
  ].join("");
  var RESOURCE_SECTION_HTML = [
    '<section id="resources" aria-label="Pixera app-store screenshot resources" class="bg-slate-50 py-20 sm:py-24">',
    '<div class="workflow-guides-shell">',
    '<div class="workflow-guides-intro">',
    '<p class="workflow-guides-kicker">High-Intent Resources</p>',
    '<h2 class="workflow-guides-title font-display">Catch the App Store screenshot demand already reaching the site.</h2>',
    '<p class="workflow-guides-copy">These practical resources answer the commercial-intent searches that are already hitting Pixera. Use them to plan, size, and polish App Store screenshot sets on Mac without overselling what the product does.</p>',
    '</div>',
    '<div class="workflow-guides-grid workflow-guides-grid-resources">',
    '<a class="workflow-guide-card workflow-resource-card" href="/blog/app-screenshots-for-app-store-2026.html">',
    '<p class="workflow-guide-label">Workflow Resource</p>',
    '<h3 class="workflow-guide-title font-display">App Screenshots for the App Store in 2026</h3>',
    '<p class="workflow-guide-body">Plan a stronger screenshot sequence, keep copy readable, and polish each frame on Mac before you upload the final set.</p>',
    '<span class="workflow-guide-cta">See the App Store screenshot guide</span>',
    '</a>',
    '<a class="workflow-guide-card workflow-resource-card" href="/blog/app-store-screenshot-sizes-2026.html">',
    '<p class="workflow-guide-label">Reference</p>',
    '<h3 class="workflow-guide-title font-display">App Store Screenshot Sizes for 2026</h3>',
    '<p class="workflow-guide-body">Use a clean Apple-referenced size table for iPhone, iPad, and Mac screenshot sets before you export and upload.</p>',
    '<span class="workflow-guide-cta">See the screenshot size reference</span>',
    '</a>',
    '</div>',
    '</div>',
    '</section>'
  ].join("");
  var PIXERA_ORGANIZATION_SCHEMA = {
    "@context": "https://schema.org",
    "@type": "Organization",
    name: "Pixera",
    url: "https://pixeratools.com/",
    logo: "https://pixeratools.com/icon-512.png",
    description: "Pixera is a macOS screenshot editor for styling, annotation, privacy redaction, and polished export-ready screenshots.",
    email: "hello@pixeratools.com"
  };
  var PIXERA_WEBSITE_SCHEMA = {
    "@context": "https://schema.org",
    "@type": "WebSite",
    name: "Pixera",
    url: "https://pixeratools.com/"
  };

  function ensureGtag() {
    window.dataLayer = window.dataLayer || [];
    if (typeof window.gtag !== "function") {
      window.gtag = function () {
        window.dataLayer.push(arguments);
      };
    }
  }

  function track(eventName, params) {
    ensureGtag();
    window.gtag("event", eventName, params || {});
  }

  function normalizePath(pathname) {
    if (!pathname) {
      return "/";
    }

    if (pathname.charAt(pathname.length - 1) === "/") {
      return pathname;
    }

    if (pathname.indexOf(".html") !== -1) {
      return pathname;
    }

    return pathname.charAt(pathname.length - 1) === "/" ? pathname : pathname + "/";
  }

  function upsertMeta(selector, attribute, value) {
    var element;

    if (!value) {
      return;
    }

    element = document.head.querySelector(selector);

    if (!element) {
      element = document.createElement("meta");

      if (selector.indexOf('name="') !== -1) {
        element.setAttribute("name", selector.split('name="')[1].split('"')[0]);
      } else if (selector.indexOf('property="') !== -1) {
        element.setAttribute("property", selector.split('property="')[1].split('"')[0]);
      }

      document.head.appendChild(element);
    }

    element.setAttribute(attribute, value);
  }

  function upsertJsonLd(id, value) {
    var element;

    if (!value) {
      return;
    }

    element = document.getElementById(id);

    if (!element) {
      element = document.createElement("script");
      element.type = "application/ld+json";
      element.id = id;
      document.head.appendChild(element);
    }

    element.textContent = JSON.stringify(value);
  }

  function removeRestrictedSchema() {
    var scripts = document.querySelectorAll('script[type="application/ld+json"]');

    Array.prototype.forEach.call(scripts, function (script) {
      try {
        var value = JSON.parse(script.textContent || "{}");

        if (value && (value["@type"] === "FAQPage" || value["@type"] === "HowTo")) {
          script.parentNode.removeChild(script);
        }
      } catch (error) {
        // Ignore invalid JSON-LD blocks; this function only removes known disallowed types.
      }
    });
  }

  function ensureEntitySchema() {
    removeRestrictedSchema();
    upsertJsonLd("pixera-organization-schema", PIXERA_ORGANIZATION_SCHEMA);
    upsertJsonLd("pixera-website-schema", PIXERA_WEBSITE_SCHEMA);
  }

  function syncMetadata() {
    var path = normalizePath(window.location.pathname);
    var metadata = PAGE_METADATA[path];
    var canonical;

    if (!metadata) {
      return;
    }

    document.title = metadata.title;
    upsertMeta('meta[name="description"]', "content", metadata.description);
    upsertMeta('meta[name="keywords"]', "content", metadata.keywords);
    upsertMeta('meta[property="og:title"]', "content", metadata.title);
    upsertMeta('meta[property="og:description"]', "content", metadata.description);
    upsertMeta('meta[property="og:image"]', "content", "https://pixeratools.com/social-card.jpg");
    upsertMeta('meta[property="og:image:width"]', "content", "1200");
    upsertMeta('meta[property="og:image:height"]', "content", "630");
    upsertMeta('meta[property="og:locale"]', "content", "en_US");
    upsertMeta('meta[property="og:site_name"]', "content", "Pixera");
    upsertMeta('meta[name="twitter:title"]', "content", metadata.title);
    upsertMeta('meta[name="twitter:description"]', "content", metadata.description);
    upsertMeta('meta[name="twitter:image"]', "content", "https://pixeratools.com/social-card.jpg");

    canonical = document.head.querySelector('link[rel="canonical"]');
    if (!canonical) {
      canonical = document.createElement("link");
      canonical.setAttribute("rel", "canonical");
      document.head.appendChild(canonical);
    }
    canonical.setAttribute("href", metadata.canonical);
  }

  function stabilizeMetadata() {
    if (metadataStabilized) {
      return;
    }

    metadataStabilized = true;
    syncMetadata();
    window.setTimeout(syncMetadata, 0);
    window.setTimeout(syncMetadata, 150);
    window.setTimeout(syncMetadata, 600);
    window.setTimeout(syncMetadata, 1500);
    window.setTimeout(syncMetadata, 3000);
    window.addEventListener("load", syncMetadata);
  }

  function ensureGuideHub() {
    var path = normalizePath(window.location.pathname);
    var features;

    if (path !== "/" || document.getElementById("guides")) {
      return;
    }

    features = document.getElementById("features");
    if (!features || !features.parentNode) {
      return;
    }

    features.insertAdjacentHTML("beforebegin", GUIDE_SECTION_HTML);
  }

  function ensureResourceHub() {
    var guides = document.getElementById("guides");
    var features = document.getElementById("features");

    if (normalizePath(window.location.pathname) !== "/" || document.getElementById("resources")) {
      return;
    }

    if (guides && guides.parentNode) {
      guides.insertAdjacentHTML("afterend", RESOURCE_SECTION_HTML);
      return;
    }

    if (features && features.parentNode) {
      features.insertAdjacentHTML("beforebegin", RESOURCE_SECTION_HTML);
    }
  }

  function stabilizeHomepage() {
    ensureGuideHub();
    ensureResourceHub();
    window.setTimeout(ensureGuideHub, 0);
    window.setTimeout(ensureResourceHub, 0);
    window.setTimeout(ensureGuideHub, 150);
    window.setTimeout(ensureResourceHub, 150);
    window.setTimeout(ensureGuideHub, 600);
    window.setTimeout(ensureResourceHub, 600);
    window.setTimeout(ensureGuideHub, 1500);
    window.setTimeout(ensureResourceHub, 1500);
    window.setTimeout(ensureGuideHub, 3000);
    window.setTimeout(ensureResourceHub, 3000);
  }

  function findSection(node) {
    var current = node;

    while (current && current !== document.body) {
      if (current.id) {
        return current.id;
      }

      if (current.tagName) {
        var tag = current.tagName.toLowerCase();
        if (tag === "header" || tag === "footer" || tag === "nav" || tag === "main") {
          return tag;
        }
      }

      current = current.parentElement;
    }

    return "page";
  }

  function getHref(node) {
    return (node && node.getAttribute("href")) || "";
  }

  function bindDelegatedClicks(matcher, eventName, builder) {
    document.addEventListener("click", function (event) {
      var node = event.target && event.target.closest ? event.target.closest("a") : null;

      if (!node || !matcher(node)) {
        return;
      }

      track(eventName, builder(node));
    }, true);
  }

  function getPathname(node) {
    try {
      return normalizePath(new URL(node.href, window.location.origin).pathname);
    } catch (error) {
      return "";
    }
  }

  function resolveResourceSlug(pathname) {
    var normalizedPath = pathname || "";

    if (!normalizedPath) {
      return "";
    }

    if (RESOURCE_PATHS[normalizedPath]) {
      return RESOURCE_PATHS[normalizedPath];
    }

    if (normalizedPath.indexOf("/blog/") === 0 && normalizedPath.indexOf(".html") !== -1) {
      return normalizedPath.replace(/^\/blog\//, "").replace(/\.html$/, "");
    }

    return "";
  }

  function isHalfVisible(element) {
    var rect;
    var visibleTop;
    var visibleBottom;
    var visibleHeight;

    if (!element) {
      return false;
    }

    rect = element.getBoundingClientRect();
    visibleTop = Math.max(rect.top, 0);
    visibleBottom = Math.min(rect.bottom, window.innerHeight || document.documentElement.clientHeight);
    visibleHeight = Math.max(0, visibleBottom - visibleTop);

    if (rect.height <= 0) {
      return false;
    }

    return visibleHeight / rect.height >= 0.5;
  }

  function observePricing() {
    function check() {
      var pricing = document.getElementById("pricing");

      if (!seen.view_pricing && isHalfVisible(pricing)) {
        seen.view_pricing = true;
        track("view_pricing", {
          page_type: "landing_page",
          section_id: "pricing"
        });
        window.removeEventListener("scroll", check);
        window.removeEventListener("resize", check);
      }
    }

    window.addEventListener("scroll", check, { passive: true });
    window.addEventListener("resize", check);
    window.setTimeout(check, 0);
    window.setTimeout(check, 1000);
  }

  function initTracking() {
    if (initialized) {
      return;
    }

    initialized = true;
    stabilizeMetadata();
    stabilizeHomepage();
    ensureEntitySchema();

    bindDelegatedClicks(function (node) {
      var href = getHref(node);
      return href.indexOf("Pixera") !== -1 && href.indexOf(".dmg") !== -1;
    }, "download_installer", function (node) {
      return {
        cta_location: findSection(node),
        link_url: node.href,
        platform: "macOS"
      };
    });

    bindDelegatedClicks(function (node) {
      return getHref(node).indexOf("lemonsqueezy.com/buy") !== -1;
    }, "begin_checkout", function (node) {
      return {
        cta_location: findSection(node),
        currency: "USD",
        item_category: "desktop_app",
        item_name: "Pixera Premium",
        value: 19.99
      };
    });

    bindDelegatedClicks(function (node) {
      return getHref(node).indexOf("mailto:hello@pixeratools.com") === 0;
    }, "generate_lead", function (node) {
      return {
        cta_location: findSection(node),
        method: "email",
        link_url: node.href
      };
    });

    bindDelegatedClicks(function (node) {
      return !!GUIDE_PATHS[getPathname(node)];
    }, "open_guide", function (node) {
      var guidePath = getPathname(node);
      return {
        cta_location: findSection(node),
        guide_slug: GUIDE_PATHS[guidePath],
        link_url: node.href
      };
    });

    bindDelegatedClicks(function (node) {
      return !!resolveResourceSlug(getPathname(node));
    }, "open_resource", function (node) {
      var resourcePath = getPathname(node);
      var resourceSlug = resolveResourceSlug(resourcePath);
      return {
        cta_location: findSection(node),
        resource_slug: resourceSlug,
        resource_type: "blog_article",
        link_url: node.href
      };
    });

    observePricing();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initTracking);
  } else {
    initTracking();
  }
})();
