/* Cloudflare Pages advanced-mode worker. Never expose or persist Google review data. */
const ALIASES = /*__HTML_ALIASES__*/{};
const HOST = "abrprotowing.com";
const PREVIEW = "abr-pro-towing.pages.dev";
const PLACE = "ChIJgyIjHDrhvq4R4Gz5Axv73Us";
const FIELDS = "rating,userRatingCount,reviews,googleMapsUri,attributions";
const INTERNAL = "/site-html-assets/";
const DAILY_DEFAULT = 100;
const reverse = Object.fromEntries(Object.keys(ALIASES).filter(p=>!p.startsWith("/google")).map(p=>[p.slice(0,-5),p]));
function headers(response, url, api=false) {
  const h = new Headers(response.headers);
  h.set("X-Content-Type-Options","nosniff");
  h.set("Referrer-Policy","strict-origin-when-cross-origin");
  h.set("X-Frame-Options","DENY");
  h.set("Permissions-Policy","camera=(), microphone=(), geolocation=()");
  if (url.hostname === HOST) h.set("Strict-Transport-Security","max-age=86400");
  if (url.hostname !== HOST || api) h.set("X-Robots-Tag","noindex, nofollow");
  if(api){h.set("Cache-Control","no-store, private");h.delete("Access-Control-Allow-Origin");}
  return new Response(response.body,{status:response.status,statusText:response.statusText,headers:h});
}
const json=(data,status=200)=>Response.json(data,{status,headers:{"Cache-Control":"no-store, private"}});
const error=(status)=>json({error:"Reviews temporarily unavailable"},status);
async function reserve(env) {
  // Atomic global daily cap across all locations, including previews. Fail closed.
  if (!env.REVIEWS_DB) return false;
  const raw=Number(env.REVIEWS_DAILY_LIMIT || DAILY_DEFAULT);
  const limit=Number.isInteger(raw) && raw>0 && raw<=1000 ? raw : DAILY_DEFAULT;
  const day=new Date().toISOString().slice(0,10);
  await env.REVIEWS_DB.prepare("CREATE TABLE IF NOT EXISTS review_budget (day TEXT PRIMARY KEY, used INTEGER NOT NULL)").run();
  const row=await env.REVIEWS_DB.prepare("INSERT INTO review_budget(day,used) VALUES (?,1) ON CONFLICT(day) DO UPDATE SET used=used+1 WHERE used < ? RETURNING used").bind(day,limit).first();
  return !!row;
}
function normalize(data) {
  const arr=Array.isArray(data.reviews)?data.reviews:[];
  return {
    rating:typeof data.rating==="number"?data.rating:null,
    userRatingCount:typeof data.userRatingCount==="number"?data.userRatingCount:null,
    googleMapsURI:data.googleMapsUri,
    reviews:arr.slice(0,5).map(r=>({
      rating:r.rating,text:r.text?.text || r.originalText?.text || "",publishTime:r.publishTime,
      googleMapsURI:r.googleMapsUri,
      authorAttribution:{displayName:r.authorAttribution?.displayName,uri:r.authorAttribution?.uri,photoURI:r.authorAttribution?.photoUri}
    })),
    attributions:(Array.isArray(data.attributions)?data.attributions:[]).map(a=>({provider:a.provider,providerURI:a.providerUri}))
  };
}
async function reviews(request,env,url) {
  if(request.method!=="POST") return new Response(null,{status:405,headers:{Allow:"POST"}});
  if(url.search || request.headers.get("Origin")!==url.origin || request.headers.get("X-ABR-Reviews")!=="1" || (request.headers.get("Sec-Fetch-Site")||"same-origin")!=="same-origin") return error(403);
  if(url.hostname!==HOST && url.hostname!==PREVIEW) return error(403);
  if(env.REVIEWS_ENABLED!=="1" || !env.GOOGLE_PLACES_API_KEY || !env.REVIEWS_DB) return error(503);
  try {
    if(!await reserve(env)) return error(429);
    const response=await fetch("https://places.googleapis.com/v1/places/"+PLACE+"?languageCode=en",{
      headers:{"X-Goog-Api-Key":env.GOOGLE_PLACES_API_KEY,"X-Goog-FieldMask":FIELDS},
      redirect:"manual",signal:AbortSignal.timeout(10000)
    });
    if(!response.ok) return error(502);
    return json(normalize(await response.json()));
  } catch { return error(503); }
}
export default {
  async fetch(request,env) {
    const url=new URL(request.url);
    const path=url.pathname;
    if(url.hostname==="www."+HOST){url.hostname=HOST;return Response.redirect(url.href,301);}
    if(path==="/api/reviews") return headers(await reviews(request,env,url),url,true);
    if(path.startsWith("/api/") || path.startsWith(INTERNAL) || path.startsWith("/_src/") || path.startsWith("/.git")) return headers(new Response("Not found",{status:404}),url);
    if(!["GET","HEAD"].includes(request.method)) return headers(new Response(null,{status:405,headers:{Allow:"GET, HEAD"}}),url);
    if(Object.hasOwn(reverse,path)){url.pathname=reverse[path];return Response.redirect(url.href,301);}
    if(Object.hasOwn(ALIASES,path)){
      const asset=new URL(request.url);
      asset.pathname=ALIASES[path];asset.search="";
      const result=await env.ASSETS.fetch(new Request(asset,{method:request.method}));
      if(result.status!==200) return headers(new Response("Page unavailable",{status:503}),url);
      const h=new Headers(result.headers);
      h.set("Content-Type",path.startsWith("/google")?"text/plain; charset=utf-8":"text/html; charset=utf-8");
      return headers(new Response(result.body,{status:200,headers:h}),url);
    }
    return headers(await env.ASSETS.fetch(request),url);
  }
};
