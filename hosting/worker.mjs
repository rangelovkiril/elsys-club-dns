const SOURCE = 'https://raw.githubusercontent.com/rangelovkiril/elsys-club-dns/main/index.html';

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (!['GET', 'HEAD'].includes(request.method)) return new Response('Method not allowed.', { status: 405 });
    if (!['/', '/index.html'].includes(url.pathname)) return new Response('Not found.', { status: 404 });

    let response;
    let source = 'repository';
    try {
      response = await fetch(SOURCE, {
        redirect: 'error', signal: AbortSignal.timeout(5000),
        cf: { cacheEverything: true, cacheTtlByStatus: { '200': 60, '400-599': 0 } },
      });
    } catch { /* The bundled approved snapshot remains available during GitHub failures. */ }
    if (!response || response.status !== 200) {
      await response?.body?.cancel();
      source = 'bootstrap';
      response = await env.ASSETS.fetch(new Request(new URL('/index.html', url), { method: 'GET' }));
    }
    if (response.status !== 200) return new Response('Publication unavailable.', { status: 503 });
    if (request.method === 'HEAD') await response.body?.cancel();
    return new Response(request.method === 'HEAD' ? null : response.body, {
      headers: {
        'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store',
        'X-Content-Type-Options': 'nosniff', 'Referrer-Policy': 'no-referrer',
        'X-Clubs-Source': source,
      },
    });
  },
};
