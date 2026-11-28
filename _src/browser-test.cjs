const { chromium } = require("playwright");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const base = "http://127.0.0.1:8000";
(async () => {
 const browser = await chromium.launch({headless:true, executablePath:process.env.CHROME_PATH || undefined,args:['--no-sandbox']});
 try {
  const page = await browser.newPage({viewport:{width:375,height:812}});
  const errors=[];
  page.on("pageerror", e=>errors.push(e.message));
  await page.route("https://maps.google.com/**",r=>r.abort());
  const urls = fs.readFileSync("sitemap.xml","utf8").match(/<loc>[^<]+<\/loc>/g).map(s=>s.slice(5,-6).replace("https://abrprotowing.com",base));
  for (const width of [320,375,768,1280]) {
   await page.setViewportSize({width,height:900});
   for (const url of urls) {
    const response=await page.goto(url,{waitUntil:"domcontentloaded"});
    assert.equal(response.status(),200,url);
    assert.equal(await page.locator("h1").count(),1,url);
    const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+2);
    assert.equal(overflow,false,"Horizontal overflow: "+width+" "+url);
    assert.ok(await page.locator('a[href="tel:+16478925167"]').first().count());
    if(width<900) assert.ok(await page.locator(".callbar").isVisible());
   }
   await page.goto(base+"/",{waitUntil:"domcontentloaded"});
   if(await page.locator(".nav-toggle").isVisible()){
    await page.locator(".nav-toggle").click();
    assert.equal(await page.locator(".nav-toggle").getAttribute("aria-expanded"),"true");
    assert.ok(await page.locator("#nav a").first().isVisible());
    await page.locator(".nav-toggle").click();
    assert.equal(await page.locator(".nav-toggle").getAttribute("aria-expanded"),"false");
   }
   await page.screenshot({path:"browser-evidence/home-"+width+".png",fullPage:true});
  }
  await page.goto(base+"/reviews.html");
  assert.ok(await page.locator('a[href="https://share.google/GNsj14FYJZ46z7Qpz"]').count());
  assert.equal(await page.locator(".live-reviews").count(),1,"Live reviews must be configured");
  assert.equal(await page.locator(".live-reviews").getAttribute("data-place"),"ChIJgyIjHDrhvq4R4Gz5Axv73Us");
  assert.ok(await page.locator('a[href="https://g.page/r/CeBs-QMb-91LEAE/review"]').count());
  // Mock API response; deliberately include HTML-looking review text to exercise safe rendering.
  await page.route("https://maps.googleapis.com/maps/api/js?*",r=>r.fulfill({contentType:"application/javascript",body:`
   window.google={maps:{importLibrary:async()=>({Place:class{
   async fetchFields(){this.rating=4.7;this.userRatingCount=23;this.googleMapsURI="https://www.google.com/maps";
   this.attributions=[];this.reviews=[{rating:5,text:"<img src=x onerror=alert(1)>",publishTime:new Date("2026-11-01"),authorAttribution:{displayName:"Test Reviewer",uri:"https://www.google.com/maps"}}];}
   }})}};window.abrGoogleReady();`}));
  await page.locator(".live-reviews button").click();
  await page.locator(".google-results .review").waitFor();
  assert.match(await page.locator(".google-results").innerText(),/4\.7 \/ 5 · 23 ratings/);
  assert.ok((await page.locator(".google-results").innerText()).includes("<img src=x onerror=alert(1)>"));
  assert.equal(await page.locator(".google-results img").count(),0);
  await page.screenshot({path:"browser-evidence/reviews-mocked.png",fullPage:true});
  // Form contract only: intercept the outbound request, never send a real message.
  await page.route("https://formsubmit.co/**",async r=>{
   assert.equal(r.request().method(),"POST");
   assert.match(r.request().postData(),/test/i);
   await r.fulfill({status:200,contentType:"text/html",body:"<h1>Mock form received</h1>"});
  });
  await page.goto(base+"/contact.html");
  await page.locator("#f-name").fill("Test Only");
  await page.locator("#f-phone").fill("6475550100");
  await page.locator("#f-where").fill("Test pickup");
  await page.locator('button[type="submit"]').click();
  await page.getByRole("heading",{name:"Mock form received"}).waitFor();
  assert.deepEqual(errors,[]);
  console.log("PASS: "+urls.length+" pages at 4 widths, mobile menu, phone CTA, Google fallback, mocked review rendering/XSS safety, intercepted contact form");
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
