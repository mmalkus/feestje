const C="speurtocht-v9";
const FILES=["./","index.html","manifest.webmanifest","icon.svg"];
self.addEventListener("install",e=>{e.waitUntil(caches.open(C).then(c=>c.addAll(FILES)));self.skipWaiting();});
self.addEventListener("activate",e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==C).map(k=>caches.delete(k)))));self.clients.claim();});
self.addEventListener("fetch",e=>{
  if(e.request.method!=="GET")return;
  // Only the game itself and its fonts are cached; AI API calls (e.g. /models) must always hit the network.
  const u=new URL(e.request.url);
  if(u.origin!==self.location.origin && !/^fonts\.(googleapis|gstatic)\.com$/.test(u.hostname))return;
  e.respondWith(caches.match(e.request).then(hit=>hit||fetch(e.request).then(r=>{
    const copy=r.clone(); caches.open(C).then(c=>c.put(e.request,copy)); return r;
  }).catch(()=>caches.match("index.html"))));
});
