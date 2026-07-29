// Serverless endpoint: logs an anonymous draft-page visit to a Google Sheet.
//
// Each draft page fires a SAME-ORIGIN beacon to /api/hit (navigator.sendBeacon,
// with an <img> pixel fallback) — no third-party host is ever contacted from
// the page itself, so the drafts stay first-party only. This function enriches
// the hit with the request's user-agent and Vercel geo headers and forwards it
// to a Google Apps Script web app bound to the tracking sheet. Set in Vercel:
//   VISIT_SHEET_ENDPOINT  the Apps Script /exec URL
// See reference/visit-tracking/README.md. Until that var is set the endpoint
// quietly no-ops, so the drafts never break while it's being wired up.

module.exports = async (req, res) => {
  // Accept a sendBeacon JSON body (POST) or an <img> query fallback (GET).
  let data = {};
  if (req.method === 'POST') {
    let b = req.body;
    if (typeof b === 'string') { try { b = JSON.parse(b); } catch (e) { b = {}; } }
    if (b && typeof b === 'object') data = b;
  } else {
    data = req.query || {};
  }

  const h = req.headers || {};
  const city = h['x-vercel-ip-city'];
  const hit = {
    slug: String(data.slug || '').slice(0, 120),
    path: String(data.path || '').slice(0, 200),
    ref: String(data.ref || '').slice(0, 400),
    country: h['x-vercel-ip-country'] || '',
    region: h['x-vercel-ip-country-region'] || '',
    city: city ? decodeURIComponent(city) : '',
    ua: String(h['user-agent'] || '').slice(0, 400)
  };

  const endpoint = process.env.VISIT_SHEET_ENDPOINT;
  if (endpoint && hit.slug) {
    const ctrl = new AbortController();
    const t = setTimeout(() => ctrl.abort(), 4000);
    try {
      await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(hit),
        signal: ctrl.signal
      });
    } catch (e) {
      // Never let a logging failure surface to the visitor.
    } finally {
      clearTimeout(t);
    }
  }

  res.setHeader('Cache-Control', 'no-store');
  if (req.method === 'GET') {
    // 1x1 transparent GIF for the no-sendBeacon <img> fallback.
    res.setHeader('Content-Type', 'image/gif');
    return res.status(200).send(
      Buffer.from('R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7', 'base64')
    );
  }
  return res.status(204).end();
};
