(function () {
  "use strict";

  const STORAGE_KEY = "bertolli-cart-v1";
  const API_BASE_URL = String(window.BERTOLLI_API_URL || "").replace(/\/$/, "");

  const PRODUCT = {
    id: "bertolli-pro-900",
    name: "Bertolli Pro 900",
    price: 4990000,
    currency: "COP"
  };

  const elements = {};
  let cart = loadCart();

  function loadCart() {
    try {
      const stored = JSON.parse(localStorage.getItem(STORAGE_KEY));
      if (stored && typeof stored.quantity === "number") {
        return { quantity: Math.max(0, stored.quantity) };
      }
    } catch (error) {
      localStorage.removeItem(STORAGE_KEY);
    }

    return { quantity: 0 };
  }

  function saveCart() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(cart));
  }

  function formatMoney(value) {
    return new Intl.NumberFormat("es-CO", {
      style: "currency",
      currency: PRODUCT.currency,
      maximumFractionDigits: 0
    }).format(value);
  }

  function subtotal() {
    return cart.quantity * PRODUCT.price;
  }

  function setFeedback(message, state) {
    if (!elements.feedback) return;
    elements.feedback.textContent = message;
    elements.feedback.dataset.state = state || "";
  }

  function hasBackend() {
    return (
      API_BASE_URL &&
      (API_BASE_URL.startsWith("https://") ||
        API_BASE_URL.startsWith("http://localhost") ||
        API_BASE_URL.startsWith("http://127.0.0.1"))
    );
  }

  function renderCart() {
    const count = String(cart.quantity);
    const total = subtotal();
    const hasItems = cart.quantity > 0;

    if (elements.count) elements.count.textContent = count;
    if (elements.quantity) elements.quantity.textContent = count;
    if (elements.subtotal) elements.subtotal.textContent = `${formatMoney(total)} COP`;
    if (elements.summaryText) {
      elements.summaryText.textContent = hasItems
        ? `${cart.quantity} unidad${cart.quantity === 1 ? "" : "es"} de ${PRODUCT.name}.`
        : "No hay productos agregados.";
    }

    if (elements.decrement) elements.decrement.disabled = !hasItems;
    if (elements.clear) elements.clear.disabled = !hasItems;
    if (elements.checkout) elements.checkout.disabled = !hasItems;
  }

  function addProduct() {
    cart.quantity += 1;
    saveCart();
    renderCart();
    setFeedback("Producto agregado al carrito local.", "success");
  }

  function decrementProduct() {
    cart.quantity = Math.max(0, cart.quantity - 1);
    saveCart();
    renderCart();
    setFeedback(cart.quantity ? "Cantidad actualizada." : "Carrito vacio.", "success");
  }

  function clearCart() {
    cart = { quantity: 0 };
    saveCart();
    renderCart();
    setFeedback("Carrito limpiado.", "success");
  }

  async function continueToCheckout() {
    if (!cart.quantity) {
      setFeedback("Agrega el producto antes de solicitar compra.", "error");
      return;
    }

    if (hasBackend()) {
      try {
        elements.checkout.disabled = true;
        setFeedback("Preparando checkout seguro...", "");

        const leadEmail = document.getElementById("lead-email")?.value.trim() || null;
        const response = await fetch(`${API_BASE_URL}/api/checkout/create-session`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            product_id: PRODUCT.id,
            quantity: cart.quantity,
            customer_email: leadEmail
          })
        });

        if (!response.ok) throw new Error("Checkout endpoint failed");

        const data = await response.json();
        if (data && typeof data.url === "string") {
          window.location.assign(data.url);
          return;
        }

        throw new Error("Checkout URL missing");
      } catch (error) {
        setFeedback("No se pudo abrir Stripe. Continuamos con cotizacion local.", "error");
      } finally {
        elements.checkout.disabled = false;
      }
    }

    const leadMessage = document.getElementById("lead-message");
    if (leadMessage && !leadMessage.value.trim()) {
      leadMessage.value = `Quiero solicitar compra de ${cart.quantity} unidad(es) de Bertolli Pro 900. Subtotal: ${formatMoney(subtotal())} COP.`;
    }

    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    document.getElementById("cotizacion")?.scrollIntoView({
      behavior: prefersReducedMotion ? "auto" : "smooth",
      block: "start"
    });
    setFeedback("Completa tus datos para continuar a cotizacion.", "success");
  }

  function bindCart() {
    elements.count = document.getElementById("cart-count");
    elements.quantity = document.getElementById("cart-quantity");
    elements.subtotal = document.getElementById("cart-subtotal");
    elements.summaryText = document.getElementById("cart-summary-text");
    elements.feedback = document.getElementById("cart-feedback");
    elements.decrement = document.getElementById("cart-decrement");
    elements.increment = document.getElementById("cart-increment");
    elements.clear = document.getElementById("cart-clear");
    elements.checkout = document.getElementById("cart-checkout");

    document.querySelectorAll("[data-add-to-cart]").forEach((button) => {
      button.addEventListener("click", addProduct);
    });

    elements.increment?.addEventListener("click", addProduct);
    elements.decrement?.addEventListener("click", decrementProduct);
    elements.clear?.addEventListener("click", clearCart);
    elements.checkout?.addEventListener("click", continueToCheckout);

    renderCart();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bindCart);
  } else {
    bindCart();
  }
})();
