import assert from "node:assert/strict";
import fs from "node:fs";
const code=fs.readFileSync("dist/_worker.js","utf8");
const {default:worker}=await import("data:text/javascript;base64,"+Buffer.from(code).toString("base64"));
const host="https://abrprotowing.com";
let count=0,upstream=0;
const env={ASSETS:{fetch:async req=>new Response(new URL(req.url).pathname)},REVIEWS_ENABLED:"1",GOOGLE_PLACES_API_KEY:"MOCK_ONLY",REVIEWS_DAILY_LIMIT:"2",
REVIEWS_DB:{prepare:sql=>({run:async()=>({}),bind:(day,limit)=>({first:async()=>count<limit?{used:++count}:null})})}};
const realFetch=globalThis.fetch;
globalThis.fetch=async (url,opts)=>{
  upstream++; assert.match(url,/places\/ChIJgyIjHDrhvq4R4Gz5Axv73Us\?/);assert.equal(opts.headers["X-Goog-Api-Key"],"MOCK_ONLY");
  return Response.json({rating:4.9,userRatingCount:12,googleMapsUri:"https://maps.google.com/",reviews:[{rating:5,text:{text:"Test only"},authorAttribution:{displayName:"Test",photoUri:"https://example.com/photo"},googleMapsUri:"https://maps.google.com/"}]});
};
const req=(path,options)=>new Request(host+path,options);
const api=()=>req("/api/reviews",{method:"POST",headers:{Origin:host,"X-ABR-Reviews":"1","Sec-Fetch-Site":"same-origin"}});
try{
  const urls=[...fs.readFileSync("dist/sitemap.xml","utf8").matchAll(/<loc>(.*?)<\/loc>/g)].map(m=>m[1]);
  for(const url of urls){const r=await worker.fetch(new Request(url),env);assert.equal(r.status,200,url);if(url.endsWith(".html"))assert.match(await r.text(),/^\/site-html-assets\//);}
  assert.equal((await worker.fetch(req("/google9ade8f5223a858a2.html"),env)).status,200);
  assert.equal((await worker.fetch(req("/site-html-assets/contact.html.page"),env)).status,404);
  assert.equal((await worker.fetch(req("/contact"),env)).headers.get("location"),host+"/contact.html");
  assert.equal((await worker.fetch(new Request("https://abr-pro-towing.pages.dev/contact.html"),env)).headers.get("x-robots-tag"),"noindex, nofollow");
  assert.equal((await worker.fetch(req("/api/reviews"),env)).status,405);
  assert.equal((await worker.fetch(req("/api/reviews",{method:"POST"}),env)).status,403);
  assert.equal((await worker.fetch(api(),{...env,REVIEWS_DB:null})).status,503);
  const r=await worker.fetch(api(),env);assert.equal(r.status,200);assert.equal(r.headers.get("cache-control"),"no-store, private");
  const data=await r.json();assert.equal(data.reviews[0].text,"Test only");assert.equal(data.reviews[0].authorAttribution.photoURI,"https://example.com/photo");assert.ok(!JSON.stringify(data).includes("MOCK_ONLY"));
  assert.equal((await worker.fetch(api(),env)).status,200);
  assert.equal((await worker.fetch(api(),env)).status,429);assert.equal(upstream,2);
  console.log("PASS: canonical URLs, verification route, preview noindex, endpoint guards, global cap and response mapping");
}finally{globalThis.fetch=realFetch;}
