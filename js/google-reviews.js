/* Automatically fetch Google reviews near the viewport. No persistent review cache. */
(() => {
  "use strict";
  const panels = document.querySelectorAll(".live-reviews");
  if (!panels.length) return;
  let library, request;
  const safe = value => { try { const u = new URL(value); return u.protocol === "https:" ? u.href : null; } catch { return null; } };
  function el(tag, text, cls) { const n = document.createElement(tag); if (text != null) n.textContent = text; if (cls) n.className = cls; return n; }
  function link(text, url) { const href = safe(url); if (!href) return el("span", text); const a = el("a", text); a.href = href; a.target = "_blank"; a.rel = "noopener noreferrer"; return a; }
  function loadLibrary(key) {
    if (window.google?.maps?.importLibrary) return google.maps.importLibrary("places");
    if (!library) library = new Promise((resolve, reject) => {
      const script = document.createElement("script");
      const fail = error => { clearTimeout(timer); script.remove(); reject(error); };
      const timer = setTimeout(() => fail(new Error("Google Maps timeout")), 15000);
      window.abrGoogleReady = () => { clearTimeout(timer); google.maps.importLibrary("places").then(resolve, reject); };
      script.src = "https://maps.googleapis.com/maps/api/js?" + new URLSearchParams({key, loading:"async", callback:"abrGoogleReady", v:"weekly"});
      script.async = true;
      script.onerror = () => fail(new Error("Google Maps unavailable"));
      document.head.append(script);
    }).catch(error => { library = undefined; throw error; });
    return library;
  }
  function getPlace(panel) {
    if (!request) request = (async () => {
      const {Place} = await loadLibrary(panel.dataset.key);
      const place = new Place({id:panel.dataset.place, requestedLanguage:"en-CA"});
      await place.fetchFields({fields:["rating","userRatingCount","reviews","googleMapsURI","attributions"]});
      return place;
    })().catch(error => { request = undefined; throw error; });
    return request;
  }
  function stars(rating) {
    const n = Math.max(0, Math.min(5, rating));
    const s = el("span",null,"gr-stars");
    s.setAttribute("role","img"); s.setAttribute("aria-label", n + " out of 5 stars");
    const base = el("span","★★★★★","gr-stars-base"), fill = el("span","★★★★★","gr-stars-fill");
    base.setAttribute("aria-hidden","true"); fill.setAttribute("aria-hidden","true");
    fill.style.width = (n / 5 * 100) + "%"; s.append(base,fill); return s;
  }
  function render(place, target) {
    const summary = el("div",null,"gr-summary");
    const score = el("div",null,"gr-score");
    if (typeof place.rating === "number") {
      score.append(el("strong",place.rating.toFixed(1),"gr-number"));
      const meta = el("div",null,"gr-score-meta");
      meta.append(stars(place.rating),el("span",typeof place.userRatingCount === "number" ? new Intl.NumberFormat("en-CA").format(place.userRatingCount) + " Google ratings" : "Google rating","gr-count"));
      score.append(meta);
    } else score.append(el("p","No rating available."));
    const source = el("div",null,"gr-source");
    source.append(el("span","Google Maps","google-attribution"),link("View all on Google ↗",place.googleMapsURI));
    summary.append(score,source);
    const cards = el("div",null,"gr-grid");
    for (const r of place.reviews ?? []) {
      const author = r.authorAttribution;
      if (!author?.displayName) continue;
      const card = el("article",null,"gr-card");
      const header = el("div",null,"gr-author");
      const avatar = el("span",Array.from(author.displayName.trim())[0]?.toUpperCase() || "?","gr-avatar");
      avatar.setAttribute("aria-hidden","true");
      const photo = safe(author.photoURI);
      if (photo) {
        const img = el("img"); img.src = photo; img.alt = ""; img.loading = "lazy"; img.width = 44; img.height = 44;
        img.addEventListener("error",() => img.remove(),{once:true}); avatar.append(img);
      }
      const identity = el("div",null,"gr-identity");
      identity.append(link(author.displayName,author.uri));
      if (r.publishTime) {
        const date = new Date(r.publishTime);
        if (!Number.isNaN(date.getTime())) identity.append(el("time",date.toLocaleDateString("en-CA",{year:"numeric",month:"short",day:"numeric"}),"gr-date"));
      }
      header.append(avatar,identity); card.append(header);
      if (typeof r.rating === "number") card.append(stars(r.rating));
      if (r.text) {
        const body = el("p",r.text,"gr-text");
        card.append(body);
        if (r.text.length > 220) {
          const toggle = el("button","Read more","gr-expand"); toggle.type = "button";
          toggle.setAttribute("aria-expanded","false"); body.classList.add("gr-clamped");
          toggle.addEventListener("click",() => {
            const expanded = toggle.getAttribute("aria-expanded") === "true";
            toggle.setAttribute("aria-expanded",String(!expanded)); body.classList.toggle("gr-clamped",expanded);
            toggle.textContent = expanded ? "Read more" : "Show less";
          });
          card.append(toggle);
        }
      }
      if (r.googleMapsURI) { const a = link("Original review ↗",r.googleMapsURI); a.classList.add("gr-original"); card.append(a); }
      cards.append(card);
    }
    const note = el("p","Reviews supplied by Google Maps. ","gr-note");
    note.append(link("Google review policy","https://support.google.com/contributionpolicy/answer/7400114"));
    target.replaceChildren(summary,cards,note);
    for (const a of place.attributions ?? []) if (a.provider) target.append(link(a.provider,a.providerURI));
    if (!cards.children.length) cards.append(el("p","No individual reviews were returned. Visit our Google profile for more."));
  }
  function skeleton() {
    const grid = el("div",null,"gr-grid gr-skeleton");
    grid.setAttribute("aria-hidden","true");
    for(let i=0;i<3;i++){const c=el("div",null,"gr-card");c.append(el("span",null,"gr-placeholder"),el("span",null,"gr-placeholder"),el("span",null,"gr-placeholder"));grid.append(c);}
    return grid;
  }
  for (const panel of panels) {
    const button = panel.querySelector("button"), status = panel.querySelector('[role="status"]'), result = panel.querySelector(".google-results");
    let state = "idle";
    const load = async () => {
      if (state === "loading" || state === "loaded") return;
      state = "loading"; button.hidden = true; button.disabled = true;
      status.textContent = "Loading Google reviews…"; result.setAttribute("aria-busy","true"); result.replaceChildren(skeleton());
      try {
        const place = await getPlace(panel); render(place,result); state = "loaded";
        status.textContent = "Reviews loaded from Google Maps."; status.classList.add("gr-sr-only");
      } catch {
        state = "error"; result.replaceChildren(); status.textContent = "Google reviews are temporarily unavailable. Visit our Google profile or try again.";
        button.textContent = "Try again"; button.hidden = false; button.disabled = false;
      } finally { result.setAttribute("aria-busy","false"); }
    };
    button.addEventListener("click",load);
    if ("IntersectionObserver" in window) {
      const observer = new IntersectionObserver(entries => {
        if(entries.some(entry => entry.isIntersecting)){observer.disconnect();load();}
      },{rootMargin:"250px 0px",threshold:0});
      observer.observe(panel);
    } else load();
    // Hide the legacy manual button once automatic loading has been initialized.
    if (state === "idle") { button.hidden = true; status.textContent = "Google reviews will load automatically."; }
  }
})();
