const CACHE_NAME = 'opengravity-v1';

self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', (event) => {
  // Minimal fetch listener to pass PWA requirements
  // In production, you'd cache the app shell here
});
