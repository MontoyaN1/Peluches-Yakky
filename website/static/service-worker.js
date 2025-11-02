// static/service-worker.js
const CACHE_NAME = 'yakky-v3';
const urlsToCache = [
    '/',
    '/static/css/style.css',
    '/static/js/funciones.js',
    '/static/img/icon.png',
    '/productos-todo',
    '/sobre-nosotros'
    // NO cachear: /login, /logout, /profile, /admin, /carrito
];

self.addEventListener('install', event => {
    console.log('🔄 Instalando Service Worker...');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('✅ Cache abierto');
                return cache.addAll(urlsToCache);
            })
    );
    self.skipWaiting();
});

self.addEventListener('fetch', event => {
    // Excluir completamente las rutas de autenticación
    const url = new URL(event.request.url);
    const excludedPaths = [
        '/login',
        '/logout',
        '/profile',
        '/adminvista',
        '/empleado',
        '/carrito'  // También excluimos carrito por las redirecciones
    ];

    // Si es una ruta excluida, NO usar cache
    if (excludedPaths.some(path => url.pathname.includes(path))) {
        console.log('🚫 Ruta excluida del cache:', url.pathname);
        event.respondWith(fetch(event.request));
        return;
    }

    // Excluir también peticiones POST y APIs
    if (event.request.method !== 'GET') {
        event.respondWith(fetch(event.request));
        return;
    }

    // Estrategia: Network First para contenido dinámico
    event.respondWith(
        fetch(event.request)
            .then(networkResponse => {
                // Solo cachear si es exitosa
                if (networkResponse.status === 200) {
                    const responseToCache = networkResponse.clone();
                    caches.open(CACHE_NAME)
                        .then(cache => {
                            cache.put(event.request, responseToCache);
                        });
                }
                return networkResponse;
            })
            .catch(() => {
                // Si falla la red, usar cache
                return caches.match(event.request)
                    .then(cachedResponse => {
                        return cachedResponse || caches.match('/');
                    });
            })
    );
});

self.addEventListener('activate', event => {
    console.log('✅ Service Worker activado');
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('🗑️ Eliminando cache viejo:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    self.clients.claim();
});