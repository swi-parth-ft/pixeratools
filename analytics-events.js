(function () {
  var seen = {};

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

  function bindClicks(selector, eventName, builder) {
    var nodes = document.querySelectorAll(selector);
    var i;

    for (i = 0; i < nodes.length; i += 1) {
      nodes[i].addEventListener("click", function (event) {
        var node = event.currentTarget;
        track(eventName, builder(node));
      });
    }
  }

  function observeOnce(element, key, eventName, params) {
    var observer;

    if (!element || seen[key] || !("IntersectionObserver" in window)) {
      return;
    }

    observer = new IntersectionObserver(function (entries) {
      var i;

      for (i = 0; i < entries.length; i += 1) {
        if (entries[i].isIntersecting && !seen[key]) {
          seen[key] = true;
          track(eventName, params);
          observer.disconnect();
          return;
        }
      }
    }, { threshold: 0.5 });

    observer.observe(element);
  }

  document.addEventListener("DOMContentLoaded", function () {
    bindClicks('a[href="/Pixera_Installer.dmg"]', "download_installer", function (node) {
      return {
        cta_location: findSection(node),
        link_url: node.href,
        platform: "macOS"
      };
    });

    bindClicks('a[href*="lemonsqueezy.com/buy"]', "begin_checkout", function (node) {
      return {
        cta_location: findSection(node),
        currency: "USD",
        item_category: "desktop_app",
        item_name: "Pixera Premium",
        value: 19.99
      };
    });

    bindClicks('a[href^="mailto:hello@pixeratools.com"]', "generate_lead", function (node) {
      return {
        cta_location: findSection(node),
        method: "email",
        link_url: node.href
      };
    });

    observeOnce(
      document.getElementById("pricing"),
      "view_pricing",
      "view_pricing",
      {
        page_type: "landing_page",
        section_id: "pricing"
      }
    );
  });
})();
