(function () {
  var seen = {};
  var initialized = false;

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

    observePricing();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initTracking);
  } else {
    initTracking();
  }
})();
