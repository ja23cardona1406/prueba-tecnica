(function () {
  "use strict";

  const API_BASE_URL = String(window.BERTOLLI_API_URL || "").replace(/\/$/, "");
  const API_TIMEOUT_MS = 4500;

  const PRODUCT_CORPUS = {
    price: "El precio referencial de lanzamiento de la Bertolli Pro 900 es $4.990.000 COP. Para cerrar compra, usa el formulario o WhatsApp para confirmar disponibilidad e instalacion.",
    warranty: "La garantia contemplada es de 24 meses limitada por defectos de fabricacion. Requiere instalacion correcta y uso segun recomendaciones del fabricante.",
    dimensions: "Sus dimensiones de referencia son 90 cm de ancho, 60 cm de fondo y 89 cm de alto.",
    materials: "La Bertolli Pro 900 usa acero inoxidable cepillado, parrillas de hierro fundido, perillas metalicas y doble vidrio templado en el horno.",
    power: "Tiene 5 quemadores con potencia combinada estimada de hasta 12,8 kW. El quemador triple corona entrega aproximadamente 3,8 kW.",
    cleaning: "Para limpieza, usa pano suave, agua tibia y jabon neutro. Evita fibras abrasivas sobre el acero inoxidable y seca al terminar.",
    installation: "La instalacion debe realizarla un tecnico certificado. Conviene validar ventilacion, presion de gas, espacio de 90 cm y conexion segun norma local.",
    gas: "Puede configurarse para gas natural o GLP usando el kit de conversion correspondiente. La conversion no debe hacerse de forma casera.",
    benefits: "Sus beneficios principales son mayor superficie de trabajo, llama potente para sellar, estabilidad con ollas pesadas, horno amplio y acabado premium para cocina abierta."
  };

  const RULES = [
    { keys: ["precio", "valor", "cuesta", "costo", "comprar", "cotizacion"], answer: PRODUCT_CORPUS.price },
    { keys: ["garantia", "garantias", "cobertura"], answer: PRODUCT_CORPUS.warranty },
    { keys: ["dimension", "dimensiones", "medida", "medidas", "tamano", "ancho", "alto", "fondo"], answer: PRODUCT_CORPUS.dimensions },
    { keys: ["material", "materiales", "acero", "inoxidable", "hierro", "vidrio"], answer: PRODUCT_CORPUS.materials },
    { keys: ["potencia", "kw", "quemador", "quemadores", "hornilla", "hornillas", "triple"], answer: PRODUCT_CORPUS.power },
    { keys: ["limpieza", "limpiar", "grasa", "mantenimiento", "cuidar"], answer: PRODUCT_CORPUS.cleaning },
    { keys: ["instalacion", "instalar", "tecnico", "conexion", "ventilacion"], answer: PRODUCT_CORPUS.installation },
    { keys: ["gas", "glp", "natural", "propano", "conversion"], answer: PRODUCT_CORPUS.gas },
    { keys: ["beneficio", "beneficios", "ventaja", "ventajas", "porque", "premium"], answer: PRODUCT_CORPUS.benefits }
  ];

  const elements = {};

  function normalize(text) {
    return text
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "");
  }

  function isApiConfigured() {
    return (
      API_BASE_URL &&
      (API_BASE_URL.startsWith("https://") ||
        API_BASE_URL.startsWith("http://localhost") ||
        API_BASE_URL.startsWith("http://127.0.0.1"))
    );
  }

  function localAnswer(question) {
    const normalized = normalize(question);
    const found = RULES.find((rule) => rule.keys.some((key) => normalized.includes(key)));

    if (found) return found.answer;

    return "Puedo ayudarte con precio, garantia, dimensiones, materiales, potencia, limpieza, instalacion, tipo de gas y beneficios de la Bertolli Pro 900. Si quieres, tambien puedes dejar tus datos para una cotizacion.";
  }

  async function fetchAssistantAnswer(question) {
    if (!isApiConfigured()) return null;

    const controller = new AbortController();
    const timeoutId = window.setTimeout(() => controller.abort(), API_TIMEOUT_MS);

    try {
      const response = await fetch(`${API_BASE_URL}/api/assistant/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: question
        }),
        signal: controller.signal
      });

      if (!response.ok) throw new Error(`Assistant API failed with status ${response.status}`);

      const data = await response.json();
      if (typeof data.answer === "string" && data.answer.trim()) return data.answer.trim();
      if (typeof data.message === "string" && data.message.trim()) return data.message.trim();
      return null;
    } finally {
      window.clearTimeout(timeoutId);
    }
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

  async function handleSubmit(event) {
    event.preventDefault();

    const question = elements.input.value.trim();
    if (!question) return;

    addMessage("user", question);
    elements.input.value = "";
    elements.submit.disabled = true;

    const pending = addMessage("bot", "Consultando...");
    const pendingText = pending.querySelector("p");

    try {
      const remoteAnswer = await fetchAssistantAnswer(question);
      pendingText.textContent = remoteAnswer || localAnswer(question);
    } catch (error) {
      pendingText.textContent = localAnswer(question);
    } finally {
      elements.submit.disabled = false;
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
