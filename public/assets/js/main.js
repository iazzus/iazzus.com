/* ==========================================================================
   main.js — IAZZUS.com
   Progressive enhancement only. Every page is fully readable and navigable
   with this file blocked. No dependencies, no build step.

   Modules
     1. Header scroll state
     2. Mobile navigation
     3. Scroll reveal
     4. Current year in the footer
     5. Contact form validation
     6. Contact topic prefill
   ========================================================================== */

(function () {
  "use strict";

  /* ------------------------------------------------------------------------
     Configuration

     CONTACT_ENDPOINT stays empty until a real backend exists (for example a
     Cloudflare Worker or Pages Function at /api/contact). While it is empty
     the form validates but reports honestly that it cannot send yet — it
     never pretends a message was delivered. See README "Contact form".
     ------------------------------------------------------------------------ */
  var CONTACT_ENDPOINT = "";

  var prefersReducedMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)"
  );

  /* ========================================================================
     1. Header scroll state
     ======================================================================== */

  function initHeaderScroll() {
    var header = document.querySelector("[data-header]");
    if (!header) return;

    var ticking = false;

    function update() {
      header.classList.toggle("is-scrolled", window.scrollY > 8);
      ticking = false;
    }

    window.addEventListener(
      "scroll",
      function () {
        if (ticking) return;
        ticking = true;
        window.requestAnimationFrame(update);
      },
      { passive: true }
    );

    update();
  }

  /* ========================================================================
     2. Mobile navigation
     ======================================================================== */

  function initNav() {
    var toggle = document.querySelector("[data-nav-toggle]");
    var nav = document.querySelector("[data-nav]");
    if (!toggle || !nav) return;

    var root = document.documentElement;
    var desktopQuery = window.matchMedia("(min-width: 56.25em)");
    var isOpen = false;

    function focusableItems() {
      return Array.prototype.filter.call(
        nav.querySelectorAll('a[href], button:not([disabled])'),
        function (el) {
          return el.offsetParent !== null;
        }
      );
    }

    function open() {
      isOpen = true;
      nav.classList.add("is-open");
      toggle.setAttribute("aria-expanded", "true");
      toggle.setAttribute("aria-label", "Close menu");
      root.classList.add("is-nav-open");

      var items = focusableItems();
      if (items.length) items[0].focus();
    }

    function close(returnFocus) {
      if (!isOpen) return;
      isOpen = false;
      nav.classList.remove("is-open");
      toggle.setAttribute("aria-expanded", "false");
      toggle.setAttribute("aria-label", "Open menu");
      root.classList.remove("is-nav-open");
      if (returnFocus) toggle.focus();
    }

    toggle.addEventListener("click", function () {
      if (isOpen) {
        close(false);
      } else {
        open();
      }
    });

    // Escape closes and hands focus back to the button.
    document.addEventListener("keydown", function (event) {
      if (!isOpen) return;

      if (event.key === "Escape") {
        event.preventDefault();
        close(true);
        return;
      }

      // Keep Tab inside the panel while it is open.
      if (event.key === "Tab") {
        var items = focusableItems();
        if (!items.length) return;

        var first = items[0];
        var last = items[items.length - 1];

        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          toggle.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          toggle.focus();
        } else if (document.activeElement === toggle && !event.shiftKey) {
          event.preventDefault();
          first.focus();
        }
      }
    });

    // A click anywhere outside the panel and the button closes the menu.
    document.addEventListener("click", function (event) {
      if (!isOpen) return;
      if (nav.contains(event.target) || toggle.contains(event.target)) return;
      close(false);
    });

    // Following a link inside the panel should close it.
    nav.addEventListener("click", function (event) {
      if (event.target.closest("a")) close(false);
    });

    // Crossing into the desktop layout resets everything.
    function handleBreakpoint(event) {
      if (event.matches) close(false);
    }

    if (typeof desktopQuery.addEventListener === "function") {
      desktopQuery.addEventListener("change", handleBreakpoint);
    } else if (typeof desktopQuery.addListener === "function") {
      desktopQuery.addListener(handleBreakpoint);
    }
  }

  /* ========================================================================
     3. Scroll reveal
     ======================================================================== */

  function initReveal() {
    var items = document.querySelectorAll("[data-reveal]");
    if (!items.length) return;

    function showAll() {
      Array.prototype.forEach.call(items, function (el) {
        el.classList.add("is-visible");
      });
    }

    if (prefersReducedMotion.matches || !("IntersectionObserver" in window)) {
      showAll();
      return;
    }

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        });
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.05 }
    );

    Array.prototype.forEach.call(items, function (el) {
      observer.observe(el);
    });

    // If the user turns reduced motion on mid-session, stop animating.
    if (typeof prefersReducedMotion.addEventListener === "function") {
      prefersReducedMotion.addEventListener("change", function (event) {
        if (event.matches) {
          observer.disconnect();
          showAll();
        }
      });
    }
  }

  /* ========================================================================
     4. Footer year
     ======================================================================== */

  function initYear() {
    var targets = document.querySelectorAll("[data-current-year]");
    var year = String(new Date().getFullYear());
    Array.prototype.forEach.call(targets, function (el) {
      el.textContent = year;
    });
  }

  /* ========================================================================
     5. Contact form
     ======================================================================== */

  var EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

  function validateField(control) {
    var value = (control.value || "").trim();
    var wrapper = control.closest(".field");
    var errorEl = wrapper ? wrapper.querySelector(".field__error") : null;
    var message = "";

    if (control.hasAttribute("required") && !value) {
      message = errorEl && errorEl.dataset.empty
        ? errorEl.dataset.empty
        : "This field is required.";
    } else if (value && control.type === "email" && !EMAIL_PATTERN.test(value)) {
      message = "Enter a valid email address.";
    } else if (value && control.minLength > 0 && value.length < control.minLength) {
      message = "Please use at least " + control.minLength + " characters.";
    }

    var valid = message === "";

    if (wrapper) wrapper.classList.toggle("has-error", !valid);
    if (errorEl) errorEl.textContent = message;
    control.setAttribute("aria-invalid", valid ? "false" : "true");

    return valid;
  }

  function initContactForm() {
    var form = document.querySelector("[data-contact-form]");
    if (!form) return;

    var status = form.querySelector("[data-form-status]");
    var controls = Array.prototype.slice.call(
      form.querySelectorAll(".field__control")
    );
    var trap = form.querySelector("[data-trap]");

    // Browser-native bubbles would fight our own messages.
    form.setAttribute("novalidate", "novalidate");

    function setStatus(text, state) {
      if (!status) return;
      status.textContent = text;
      if (state) {
        status.setAttribute("data-state", state);
      } else {
        status.removeAttribute("data-state");
      }
    }

    controls.forEach(function (control) {
      // Only re-validate on input once a field has already failed, so the
      // user is not scolded while they are still typing.
      control.addEventListener("input", function () {
        var wrapper = control.closest(".field");
        if (wrapper && wrapper.classList.contains("has-error")) {
          validateField(control);
        }
      });
      control.addEventListener("blur", function () {
        if ((control.value || "").trim()) validateField(control);
      });
    });

    form.addEventListener("submit", function (event) {
      event.preventDefault();

      // Silently ignore anything that filled the honeypot.
      if (trap && trap.value) return;

      var firstInvalid = null;
      controls.forEach(function (control) {
        if (!validateField(control) && !firstInvalid) firstInvalid = control;
      });

      if (firstInvalid) {
        setStatus("Please correct the highlighted fields.", "error");
        firstInvalid.focus();
        return;
      }

      if (!CONTACT_ENDPOINT) {
        setStatus(
          "This form passed validation, but no backend is connected yet, " +
            "so nothing was sent. Message delivery is not yet configured.",
          "error"
        );
        return;
      }

      submit(form, setStatus);
    });
  }

  function submit(form, setStatus) {
    var button = form.querySelector('button[type="submit"]');
    var data = new FormData(form);
    var payload = {};

    data.forEach(function (value, key) {
      payload[key] = value;
    });

    if (button) {
      button.disabled = true;
      button.dataset.originalText = button.textContent;
      button.textContent = "Sending…";
    }
    setStatus("Sending…");

    function restore() {
      if (!button) return;
      button.disabled = false;
      if (button.dataset.originalText) {
        button.textContent = button.dataset.originalText;
      }
    }

    fetch(CONTACT_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    })
      .then(function (response) {
        if (!response.ok) throw new Error("Request failed: " + response.status);
        form.reset();
        setStatus("Message sent. I will get back to you.", "success");
      })
      .catch(function () {
        setStatus(
          "Something went wrong and the message was not sent. Please try again.",
          "error"
        );
      })
      .then(restore);
  }

  /* ========================================================================
     6. Contact topic prefill

     Pages that send people to the contact form can say what the message is
     about: /contact/?topic=coaching preselects the Coaching category.

     The value is only ever compared against the options already in the
     markup, so an arbitrary string in the query does nothing. An existing
     selection is left alone, which matters when the browser restores the
     form on a back navigation.
     ======================================================================== */

  function initTopicPrefill() {
    var select = document.querySelector("[data-contact-form] #category");
    if (!select || select.value) return;

    var topic;
    try {
      topic = new URL(window.location.href).searchParams.get("topic");
    } catch (error) {
      return;
    }
    if (!topic) return;

    var match = Array.prototype.filter.call(select.options, function (option) {
      return option.value && option.value === topic.toLowerCase();
    })[0];

    if (match) select.value = match.value;
  }

  /* ========================================================================
     Boot
     ======================================================================== */

  initHeaderScroll();
  initNav();
  initReveal();
  initYear();
  initContactForm();
  initTopicPrefill();
})();
