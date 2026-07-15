(() => {
  if (!document.querySelector('link[data-global-shell]')) {
    const css=document.createElement("link"); css.rel="stylesheet"; css.href="https://thepolka.cloud/static/css/global-shell.css"; css.dataset.globalShell="true"; document.head.append(css);
  }
  const links = [["Home","https://thepolka.cloud/#welcome","thepolka.cloud"],["Résumé Generator","https://resume-generator.thepolka.cloud/#resume","resume-generator.thepolka.cloud"],["Security Agent","https://agent.thepolka.cloud/","agent.thepolka.cloud"],["Local OS FAIRE","https://faire.thepolka.cloud/#ai","faire.thepolka.cloud"],["CAD Experience","https://cad.thepolka.cloud/#ack","cad.thepolka.cloud"],["Navigate","https://directory.thepolka.cloud/#filing","directory.thepolka.cloud"],["Boutique","https://store.thepolka.cloud/#support","store.thepolka.cloud"],["Mail","https://mail-ecosystem.thepolka.cloud/#mymail","mail-ecosystem.thepolka.cloud"]];
  const host = location.hostname.toLowerCase();
  const menu = links.map(([label, href, linkHost]) => `<a href="${href}" class="nav-link${host===linkHost?" active":""}"${host===linkHost?' aria-current="page"':""}>${label}</a>`).join("");
  let shell = document.querySelector(".app-container");
  if (!shell) {
    shell=document.createElement("div"); shell.className="app-container";
    const main=document.createElement("div"); main.className="main-column";
    const page=document.createElement("main"); page.className="page-content";
    [...document.body.children].filter(node=>node.tagName!=="SCRIPT").forEach(node=>page.append(node));
    main.append(page); shell.append(main); document.body.prepend(shell);
  }
  document.documentElement.classList.add("global-shell");
  let sidebar = shell.querySelector(".sidebar");
  if (!sidebar) { sidebar=document.createElement("aside"); sidebar.className="sidebar"; shell.prepend(sidebar); }
  if (sidebar.querySelector(".hero-ticker")) {
    const builtInNav=sidebar.querySelector(".sidebar-nav");
    if (builtInNav) builtInNav.innerHTML=menu;
    return;
  }
  sidebar.innerHTML=`<a class="global-brand" href="https://thepolka.cloud/#welcome">ThePolka.Cloud™</a><nav class="sidebar-nav" aria-label="Global navigation">${menu}</nav><div class="sidebar-bottom"><div class="language-ticker">Hello · Hola · مرحباً · 你好 · Bonjour</div><div class="sidebar-contact"><a href="mailto:info@thepolka.cloud">info@thepolka.cloud</a><a href="mailto:support@thepolka.cloud">support@thepolka.cloud</a><a href="mailto:sales@thepolka.cloud">sales@thepolka.cloud</a><a href="https://privacy.thepolka.cloud/#Shh">Privacy</a></div></div>`;
  sidebar.querySelector(".language-ticker")?.remove();
  if (!document.querySelector("style[data-language-carousel]")) {
    const carouselStyle=document.createElement("style"); carouselStyle.dataset.languageCarousel="true";
    carouselStyle.textContent=".global-shell .hero-ticker{overflow:hidden;width:100%;height:48px}.global-shell .hero-ticker .ticker-track{display:flex;width:max-content;align-items:center;gap:1.25rem;animation:polkaGreetings 20s linear infinite}.global-shell .hero-ticker .ticker-item{white-space:nowrap;font-weight:700}.global-shell .hero-ticker:hover .ticker-track{animation-play-state:paused}@keyframes polkaGreetings{to{transform:translateX(-50%)}}";
    document.head.append(carouselStyle);
  }
  sidebar.querySelector(".sidebar-nav").insertAdjacentHTML("beforebegin",`<div class="hero-ticker" aria-label="Greeting ticker"><div class="ticker-track"><span class="ticker-item">Hello</span><span class="ticker-item">Hol&aacute;</span><span class="ticker-item" lang="ar" dir="rtl">&#1605;&#1585;&#1581;&#1576;&#1575;&#1611;</span><span class="ticker-item" lang="zh">&#20320;&#22909;</span><span class="ticker-item">Bonjour</span><span class="ticker-item">Hello</span><span class="ticker-item">Hol&aacute;</span><span class="ticker-item" lang="ar" dir="rtl">&#1605;&#1585;&#1581;&#1576;&#1575;&#1611;</span><span class="ticker-item" lang="zh">&#20320;&#22909;</span><span class="ticker-item">Bonjour</span></div></div>`);
  let main=shell.querySelector(".main-column");
  if (!main) { main=document.createElement("div"); main.className="main-column"; [...shell.children].filter(node=>node!==sidebar).forEach(node=>main.append(node)); shell.append(main); }
  let footer=main.querySelector(".site-footer");
  if (!footer) { footer=document.createElement("footer"); footer.className="site-footer"; main.append(footer); }
  footer.innerHTML=`<div class="footer-contact"><a href="mailto:info@thepolka.cloud">info@thepolka.cloud</a><a href="mailto:support@thepolka.cloud">support@thepolka.cloud</a><a href="mailto:sales@thepolka.cloud">sales@thepolka.cloud</a><a href="https://privacy.thepolka.cloud/#Shh">Privacy</a></div><div class="footer-legal">ThePolka.Cloud™ · Copyright © 2019–2026. All rights reserved.</div>`;
})();
