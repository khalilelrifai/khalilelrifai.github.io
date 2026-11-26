/* On-demand Google Maps Places display. No persistent review cache. */
(() => {
  "use strict";
  const panels = document.querySelectorAll(".live-reviews");
  if (!panels.length) return;
  let library, request;
  const safe = value => { try { const u = new URL(value); return u.protocol === "https:" ? u.href : null; } catch { return null; } };
  function el(tag, text, cls) { const n = document.createElement(tag); if (text != null) n.textContent = text; if (cls) n.className = cls; return n; }
  function link(text, url) { const href = safe(url); if (!href) return el("span", text); const a = el("a", text); a.href = href; a.target = "_blank"; a.rel = "noopener noreferrer"; return a; }
  function loadLibrary(key) {
    if (!library) library = new Promise((resolve, reject) => {
      const script = document.createElement("script");
      const timer = setTimeout(() => reject(new Error("Google Maps timeout")), 15000);
      window.abrGoogleReady = () => { clearTimeout(timer); google.maps.importLibrary("places").then(resolve, reject); };
      script.src = "https://maps.googleapis.com/maps/api/js?" + new URLSearchParams({key, loading:"async", callback:"abrGoogleReady", v:"weekly"});
      script.async = true;
      script.onerror = () => { clearTimeout(timer); reject(new Error("Google Maps unavailable")); };
      document.head.append(script);
    });
    return library;
  }
  function getPlace(panel) {
    if (!request) request = (async () => {
      const {Place} = await loadLibrary(panel.dataset.key);
      const place = new Place({id:panel.dataset.place, requestedLanguage:"en-CA"});
      await place.fetchFields({fields:["rating","userRatingCount","reviews","googleMapsURI","attributions"]});
      return place;
    })();
    return request;
  }
  function render(place, target) {
    const summary = el("p", typeof place.rating === "number" ? place.rating.toFixed(1) + " / 5 · " + (place.userRatingCount ?? "—") + " ratings" : "No rating available.");
    const cards = el("div",null,"reviews all");
    for (const r of place.reviews ?? []) {
      const author = r.authorAttribution;
      if (!author?.displayName) continue;
      const card = el("article",null,"review");
      const header = el("p");
      const photo = safe(author.photoURI);
      if (photo) { const img = el("img"); img.src = photo; img.alt = ""; img.loading = "lazy"; header.append(img," "); }
      header.append(link(author.displayName,author.uri)); card.append(header);
      if (typeof r.rating === "number") card.append(el("p",r.rating + " / 5"));
      if (r.publishTime) card.append(el("p",new Date(r.publishTime).toLocaleDateString("en-CA"),"muted"));
      if (r.text) card.append(el("p",r.text));
      if (r.googleMapsURI) card.append(link("Read this review on Google Maps",r.googleMapsURI));
      cards.append(card);
    }
    const source = el("p"); source.append(link("View on Google Maps",place.googleMapsURI)," · ",link("Google review policy","https://support.google.com/contributionpolicy/answer/7400114"));
    target.replaceChildren(el("p","Google Maps","google-attribution"),summary,cards,source);
    for (const a of place.attributions ?? []) if (a.provider) target.append(link(a.provider,a.providerURI));
    if (!cards.children.length) target.append(el("p","No individual reviews were returned. Visit the Google profile for more."));
  }
  for (const panel of panels) {
    const button = panel.querySelector("button"), status = panel.querySelector('[role="status"]'), result = panel.querySelector(".google-results");
    button.addEventListener("click",async () => {
      button.disabled = true; status.textContent = "Loading Google reviews…";
      try { const place = await getPlace(panel); render(place,result); status.textContent = "Reviews loaded from Google Maps."; button.hidden = true; }
      catch { status.textContent = "Google reviews could not be loaded. Please use the Google profile link."; }
    });
  }
})();
