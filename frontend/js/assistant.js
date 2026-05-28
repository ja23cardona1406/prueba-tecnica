(function () {
  "use strict";

  const PRODUCT_CORPUS = {
    price: "El precio referencial de lanzamiento de la Bertolli Pro 900 es $4.990.000 COP. Para cerrar compra, usa el formulario o WhatsApp para confirmar disponibilidad e instalación.",
    warranty: "La garantía contemplada es de 24 meses limitada por defectos de fabricación. Requiere instalación correcta y uso según recomendaciones del fabricante.",
    dimensions: "Sus dimensiones de referencia son 90 cm de ancho, 60 cm de fondo y 89 cm de alto.",
    materials: "La Bertolli Pro 900 usa acero inoxidable cepillado, parrillas de hierro fundido, perillas metálicas y doble vidrio templado en el horno.",
    power: "Tiene 5 quemadores con potencia combinada estimada de hasta 12,8 kW. El quemador triple corona entrega aproximadamente 3,8 kW.",
    cleaning: "Para limpieza, usa paño suave, agua tibia y jabón neutro. Evita fibras abrasivas sobre el acero inoxidable y seca al terminar.",
    installation: "La instalación debe realizarla un técnico certificado. Conviene validar ventilación, presión de gas, espacio de 90 cm y conexión según norma local.",
    gas: "Puede configurarse para gas natural o GLP usando el kit de conversión correspondiente. La conversión no debe hacerse de forma casera.",
    benefits: "Sus beneficios principales son mayor superficie de trabajo, llama potente para sellar, estabilidad con ollas pesadas, horno amplio y acabado premium para cocina abierta."
  };

  const RULES = [
    { keys: ["precio", "valor", "cuesta", "costo", "comprar", "cotizacion"], answer: PRODUCT_CORPUS.price },
    { keys: ["garantia", "garantias", "cobertura"], answer: PRODUCT_CORPUS.warranty },
    { keys: ["dimension", "dimensiones", "medida", "medidas", "tamaño", "ancho", "alto", "fondo"], answer: PRODUCT_CORPUS.dimensions },
    { keys: ["material", "materiales", "acero", "inoxidable", "hierro", "vidrio"], answer: PRODUCT_CORPUS.materials },
    { keys: ["potencia", "kw", "quemador", "quemadores", "hornilla", "hornillas", "triple"], answer: PRODUCT_CORPUS.power },
    { keys: ["limpieza", "limpiar", "grasa", "mantenimiento", "cuidar"], answer: PRODUCT_CORPUS.cleaning },
    { keys: ["instalacion", "instalar", "tecnico", "conexion", "ventilacion"], answer: PRODUCT_CORPUS.installation },
    { keys: ["gas", "glp", "natural", "propano", "conversion"], answer: PRODUCT_CORPUS.gas },
    { keys: ["beneficio", "beneficios", "ventaja", "ventajas", "porque", "premium"], answer: PRODUCT_CORPUS.benefits }
  ];

  const elements = {};
  const API_BASE_URL = (
    window.BERTOLLI_API_BASE_URL ||
    window.BERTOLLI_CONFIG?.API_BASE_URL ||
    (
      window.location.hostname === "localhost" ||
      window.location.hostname === "127.0.0.1"
        ? "http://localhost:8005"
        : "https://prueba-tecnica-xe6q.onrender.com"
    )
  ).replace(/\/$/, "");

    function normalize(text) {
      return text
        .toLowerCase()
        .normalize("NFD")
        .replace(/[̀-ͯ]/g, "");
    }

  function localAnswer(question) {
    const normalized = normalize(question);
    const found = RULES.find((rule) => rule.keys.some((key) => normalized.includes(key)));

    if (found) return found.answer;

    return "Puedo ayudarte con precio, garantía, dimensiones, materiales, potencia, limpieza, instalación, tipo de gas y beneficios de la Bertolli Pro 900. ¿Hay algo específico que quieras saber?";
  }

  function addMessage(role, text) {
    const article = document.createElement("article");
    const paragraph = document.createElement("p");

    article.className = `assistant-message assistant-message--${role}`;
    paragraph.textContent = text;
    article.append(paragraph);
    elements.messages.append(article);
    elements.messages.scrollTop = elements.messages.scrollHeight;

    return article;
  }

  function setPanelOpen(open) {
    elements.panel.hidden = !open;
    elements.toggle.setAttribute("aria-expanded", String(open));
    elements.toggle.setAttribute("aria-label", open ? "Cerrar asesor inteligente" : "Abrir asesor inteligente");

    if (open) {
      window.requestAnimationFrame(() => elements.input.focus());
    } else {
      elements.toggle.focus();
    }
  }

  async function askBackend(question) {
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 45000);

    try {
      const response = await fetch(`${API_BASE_URL}/api/assistant`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: question }),
        signal: controller.signal
      });

      if (!response.ok) throw new Error(`Assistant backend failed with ${response.status}`);

      const data = await response.json();
      console.log("Assistant backend response:", data);
      console.log(`Source: ${data.source} | Model: ${data.model_used} | RAG: ${data.rag_source} | Fallback: ${data.fallback_used}`);
      return data;
    } finally {
      window.clearTimeout(timeout);
    }
  }

  async function handleSubmit(event) {
    event.preventDefault();

    const question = elements.input.value.trim();
    if (!question) return;

    addMessage("user", question);
    elements.input.value = "";
    elements.submit.disabled = true;
    elements.submit.setAttribute("aria-busy", "true");

    const pending = addMessage("bot", "Consultando asistente inteligente...");
    const pendingText = pending.querySelector("p");

    try {
      try {
        const data = await askBackend(question);
        pendingText.textContent = data.answer ?? "El backend respondió sin contenido.";
      } catch (error) {
        console.warn("Backend unavailable. Using local assistant fallback.", error);
        pendingText.textContent = localAnswer(question);
      }
    } finally {
      elements.submit.disabled = false;
      elements.submit.removeAttribute("aria-busy");
      elements.input.focus();
    }
  }

  function bindAssistant() {
    elements.toggle = document.getElementById("assistant-toggle");
    elements.panel = document.getElementById("assistant-panel");
    elements.close = document.getElementById("assistant-close");
    elements.form = document.getElementById("assistant-form");
    elements.input = document.getElementById("assistant-input");
    elements.messages = document.getElementById("assistant-messages");
    elements.submit = elements.form?.querySelector("button[type='submit']");

    if (!elements.toggle || !elements.panel || !elements.form) return;

    elements.toggle.addEventListener("click", () => setPanelOpen(elements.panel.hidden));
    elements.close.addEventListener("click", () => setPanelOpen(false));
    elements.form.addEventListener("submit", handleSubmit);

    elements.panel.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            event.preventDefault();
            setPanelOpen(false);
        }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bindAssistant);
  } else {
    bindAssistant();
  }
})();
