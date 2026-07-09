/**
 * Faire — local-ai-os chat widget
 * Drop-in, dependency-free. Mount anywhere with Faire.init({...}).
 *
 * Expects a backend endpoint at `${apiBase}/chat` that accepts:
 *   POST { message: string, history: [{role, content}, ...] }
 * and returns:
 *   { reply: string }
 * Adjust `sendMessage()` below once your real backend (port 8003) is wired up.
 */
(function (global) {
  const Faire = {};
  let state = {
    open: false,
    history: [],
    busy: false,
  };
  let opts = {};
  let els = {};

  function el(tag, attrs, ...children) {
    const node = document.createElement(tag);
    if (attrs) {
      for (const [k, v] of Object.entries(attrs)) {
        if (k === "class") node.className = v;
        else if (k.startsWith("on") && typeof v === "function") node.addEventListener(k.slice(2), v);
        else node.setAttribute(k, v);
      }
    }
    children.flat().forEach((c) => {
      if (c == null) return;
      node.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
    });
    return node;
  }

  function render(root) {
    els.bubble = el(
      "button",
      { class: "faire-bubble", "aria-label": "Open Faire chat", onclick: togglePanel },
      svgIcon()
    );

    els.messages = el("div", { class: "faire-panel__messages" });

    els.input = el("textarea", {
      class: "faire-panel__input",
      rows: "1",
      placeholder: "Ask Faire anything…",
      onkeydown: (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
          e.preventDefault();
          handleSend();
        }
      },
    });

    els.sendBtn = el(
      "button",
      { class: "faire-panel__send", onclick: handleSend, "aria-label": "Send" },
      sendIcon()
    );

    els.panel = el(
      "div",
      { class: "faire-panel" },
      el(
        "div",
        { class: "faire-panel__header" },
        el(
          "div",
          {},
          el("p", { class: "faire-panel__title" }, opts.title || "Faire"),
          el("p", { class: "faire-panel__subtitle" }, opts.subtitle || "local-ai-os")
        ),
        el("button", { class: "faire-panel__close", onclick: togglePanel, "aria-label": "Close" }, "✕")
      ),
      els.messages,
      el("div", { class: "faire-panel__inputrow" }, els.input, els.sendBtn)
    );

    root.appendChild(els.panel);
    root.appendChild(els.bubble);

    addMessage("bot", "Hi, I'm Faire — your local AI assistant. How can I help?");
  }

  function svgIcon() {
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("fill", "none");
    svg.innerHTML =
      '<path d="M4 5h16v10H7l-3 3V5z" stroke="#0b0d12" stroke-width="1.8" stroke-linejoin="round" fill="none"/>';
    return svg;
  }

  function sendIcon() {
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("width", "18");
    svg.setAttribute("height", "18");
    svg.innerHTML = '<path d="M3 11l18-7-7 18-2.5-7L3 11z" fill="#0b0d12"/>';
    return svg;
  }

  function togglePanel() {
    state.open = !state.open;
    els.panel.classList.toggle("faire-open", state.open);
    if (state.open) els.input.focus();
  }

  function addMessage(role, text) {
    const cls = role === "user" ? "faire-msg--user" : role === "error" ? "faire-msg--error" : "faire-msg--bot";
    const msgEl = el("div", { class: `faire-msg ${cls}` }, text);
    els.messages.appendChild(msgEl);
    els.messages.scrollTop = els.messages.scrollHeight;
    return msgEl;
  }

  async function handleSend() {
    const text = els.input.value.trim();
    if (!text || state.busy) return;
    els.input.value = "";
    addMessage("user", text);
    state.history.push({ role: "user", content: text });
    state.busy = true;
    els.sendBtn.disabled = true;
    const thinking = addMessage("bot", "…");

    try {
      const reply = await sendMessage(text, state.history);
      thinking.textContent = reply;
      state.history.push({ role: "assistant", content: reply });
    } catch (err) {
      thinking.remove();
      addMessage("error", "Faire couldn't reach the backend. (" + (err.message || "network error") + ")");
    } finally {
      state.busy = false;
      els.sendBtn.disabled = false;
    }
  }

  // ---- Backend call: point this at your real port-8003 service ----
  async function sendMessage(message, history) {
    const res = await fetch(`${opts.apiBase}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, history }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return data.reply ?? "(no reply field in response)";
  }

  Faire.init = function (userOpts) {
    opts = Object.assign({ apiBase: "/api", title: "Faire", subtitle: "local-ai-os", startOpen: false }, userOpts);
    const root = document.querySelector(opts.mount || "#faire-widget-root");
    if (!root) {
      console.error("Faire: mount element not found:", opts.mount);
      return;
    }
    render(root);
    const hashOpensWidget = window.location.hash === "#ai" || window.location.hash === "#chat";
    if (opts.startOpen || hashOpensWidget) togglePanel();
  };

  global.Faire = Faire;
})(window);
