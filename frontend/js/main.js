(function () {
  "use strict";

  const THEME_KEY = "bertolli-theme";
  const reduceMotionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");

  function bindThemeToggle() {
    const toggle = document.getElementById("theme-toggle");
    if (!toggle) return;

    function applyTheme(theme) {
      document.documentElement.dataset.theme = theme;
      toggle.setAttribute("aria-pressed", String(theme === "dark"));
      toggle.setAttribute("aria-label", theme === "dark" ? "Cambiar a modo claro" : "Cambiar a modo oscuro");
      document.querySelector("meta[name='theme-color']")?.setAttribute("content", theme === "dark" ? "#111411" : "#0f6b5d");
    }

    // Load saved theme from localStorage or use system preference
    let currentTheme = "light";
    try {
      const saved = localStorage.getItem(THEME_KEY);
      if (saved) {
        currentTheme = saved;
      } else if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
        currentTheme = "dark";
      }
    } catch (error) {
      // localStorage can fail in strict privacy contexts; use light theme as default
    }
    
    applyTheme(currentTheme);

    toggle.addEventListener("click", () => {
      const nextTheme = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
      try {
        localStorage.setItem(THEME_KEY, nextTheme);
      } catch (error) {
        // localStorage can fail in strict privacy contexts; theme still changes for the session.
      }
      applyTheme(nextTheme);
    });
  }

  function bindFaqAccordion() {
    const questions = Array.from(document.querySelectorAll(".faq-question"));
    if (!questions.length) return;

    function setExpanded(question, expanded) {
      const answer = document.getElementById(question.getAttribute("aria-controls"));
      question.setAttribute("aria-expanded", String(expanded));
      if (answer) answer.hidden = !expanded;
    }

    questions.forEach((question, index) => {
      question.addEventListener("click", () => {
        const isExpanded = question.getAttribute("aria-expanded") === "true";
        setExpanded(question, !isExpanded);
      });

      question.addEventListener("keydown", (event) => {
        const lastIndex = questions.length - 1;
        let targetIndex = null;

        if (event.key === "ArrowDown") targetIndex = index === lastIndex ? 0 : index + 1;
        if (event.key === "ArrowUp") targetIndex = index === 0 ? lastIndex : index - 1;
        if (event.key === "Home") targetIndex = 0;
        if (event.key === "End") targetIndex = lastIndex;

        if (targetIndex !== null) {
          event.preventDefault();
          questions[targetIndex].focus();
        }
      });
    });
  }

  function bindGallery() {
    const galleryButtons = Array.from(document.querySelectorAll(".gallery-item"));
    const toggle = document.getElementById("gallery-toggle");
    const extras = Array.from(document.querySelectorAll("[data-gallery-extra]"));
    const dialog = document.getElementById("lightbox");
    const image = document.getElementById("lightbox-image");
    const title = document.getElementById("lightbox-title");
    const closeButton = document.getElementById("lightbox-close");
    const prevButton = document.getElementById("lightbox-prev");
    const nextButton = document.getElementById("lightbox-next");
    let currentIndex = 0;
    let lastFocused = null;

    if (!galleryButtons.length || !dialog || !image || !title) return;

    function setGalleryExpanded(expanded) {
      extras.forEach((item) => {
        item.hidden = !expanded;
      });
      toggle?.setAttribute("aria-expanded", String(expanded));
      if (toggle) toggle.textContent = expanded ? "Ver menos imagenes" : "Ver galeria completa";
    }

    function showAt(index) {
      const item = galleryButtons[index];
      if (!item) return;

      currentIndex = index;
      image.src = item.dataset.src;
      image.alt = item.dataset.alt || "";
      title.textContent = item.dataset.title || "Galeria Bertolli Pro 900";
    }

    function openAt(index) {
      showAt(index);
      lastFocused = document.activeElement;

      if (typeof dialog.showModal === "function") {
        dialog.showModal();
      } else {
        dialog.setAttribute("open", "");
      }

      closeButton?.focus();
    }

    function closeDialog() {
      if (typeof dialog.close === "function" && dialog.open) {
        dialog.close();
      } else {
        dialog.removeAttribute("open");
      }

      if (lastFocused && typeof lastFocused.focus === "function") {
        lastFocused.focus();
      }
    }

    function move(step) {
      const nextIndex = (currentIndex + step + galleryButtons.length) % galleryButtons.length;
      showAt(nextIndex);
    }

    galleryButtons.forEach((button, index) => {
      button.addEventListener("click", () => openAt(index));
    });

    toggle?.addEventListener("click", () => {
      const expanded = toggle.getAttribute("aria-expanded") === "true";
      setGalleryExpanded(!expanded);
    });

    closeButton?.addEventListener("click", closeDialog);
    prevButton?.addEventListener("click", () => move(-1));
    nextButton?.addEventListener("click", () => move(1));

    dialog.addEventListener("click", (event) => {
      if (event.target === dialog) closeDialog();
    });

    dialog.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            event.preventDefault();
            closeDialog();
        }

        if (event.key === "ArrowLeft") {
            event.preventDefault();
            move(-1);
        }

        if (event.key === "ArrowRight") {
            event.preventDefault();
            move(1);
        }
    });

    setGalleryExpanded(false);
  }

  function bindLeadForm() {
    const form = document.getElementById("lead-form");
    const status = document.getElementById("lead-status");
    if (!form || !status) return;

    function setStatus(message, state) {
      status.textContent = message;
      status.dataset.state = state || "";
    }

    form.addEventListener("submit", async (event) => {
      event.preventDefault();

      if (!form.checkValidity()) {
        form.reportValidity();
        return;
      }

      const submit = form.querySelector("button[type='submit']");
      const formData = new FormData(form);
      const lead = {
        name: String(formData.get("name") || "").trim(),
        email: String(formData.get("email") || "").trim(),
        message: String(formData.get("message") || "").trim()
      };

      submit.disabled = true;
      submit.setAttribute("aria-busy", "true");
      setStatus("Procesando solicitud...", "");

      try {
        // Simulate processing delay
        await new Promise(resolve => setTimeout(resolve, 800));
        
        setStatus("Solicitud recibida. Te contactaremos a " + lead.email + " con la cotización.", "success");
        form.reset();
      } catch (error) {
        setStatus("Error al procesar la solicitud. Intenta de nuevo.", "error");
      } finally {
            submit.disabled = false;
            submit.removeAttribute("aria-busy");
        }
    });
  }

  function setCurrentYear() {
    const year = document.getElementById("current-year");
    if (year) year.textContent = String(new Date().getFullYear());
  }

  function smoothScrollFallback() {
    document.querySelectorAll('a[href^="#"]').forEach((link) => {
      link.addEventListener("click", (event) => {
        const href = link.getAttribute("href");
        if (!href || href === "#") return;

        const target = document.querySelector(href);
        if (!target || reduceMotionQuery.matches) return;

        event.preventDefault();
        target.scrollIntoView({ behavior: "smooth", block: "start" });
        history.pushState(null, "", href);
      });
    });
  }

  function init() {
    bindThemeToggle();
    bindFaqAccordion();
    bindGallery();
    bindLeadForm();
    setCurrentYear();
    smoothScrollFallback();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();