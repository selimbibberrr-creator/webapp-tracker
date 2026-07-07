const CACHE_VERSION = 'forge-tracker-v0.9-pwa.1';
const CHUNK_COUNT = 13;
const BASE_FILES = [
  './',
  './index.html',
  './manifest.webmanifest',
  './offline.html',
  './404.html',
  './version.json',
  './icons/icon.svg',
  './payload/metadata.json'
];
const PAYLOAD_FILES = Array.from({ length: CHUNK_COUNT }, (_, index) =>
  `./payload/chunk-${String(index).padStart(2, '0')}.txt`,
);
const PRECACHE = [...BASE_FILES, ...PAYLOAD_FILES];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_VERSION).then((cache) => cache.addAll(PRECACHE)).then(() => self.skipWaiting()),
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((key) => key.startsWith('forge-tracker-') && key !== CACHE_VERSION).map((key) => caches.delete(key))))
      .then(() => self.clients.claim()),
  );
});

self.addEventListener('message', (event) => {
  if (event.data?.type === 'SKIP_WAITING') self.skipWaiting();
});

self.addEventListener('fetch', (event) => {
  const request = event.request;
  if (request.method !== 'GET') return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request)
        .then((response) => {
          const clone = response.clone();
          caches.open(CACHE_VERSION).then((cache) => cache.put('./index.html', clone));
          return response;
        })
        .catch(async () => (await caches.match('./index.html')) || caches.match('./offline.html')),
    );
    return;
  }

  event.respondWith(
    caches.match(request).then((cached) => {
      const network = fetch(request)
        .then((response) => {
          if (response.ok) caches.open(CACHE_VERSION).then((cache) => cache.put(request, response.clone()));
          return response;
        })
        .catch(() => cached);
      return cached || network;
    }),
  );
});
