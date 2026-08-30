/**
 * Cloudflare Worker entry for postpaidplans.com.
 *
 * Deploys as "Workers with Static Assets" (same model as uae-premium-numbers):
 * the static site is served from the ASSETS binding; the worker only adds a
 * couple of dynamic routes.
 *
 * Routes:
 *   GET /r?text=...   -> WhatsApp deep-link redirect (handy for ad short-links)
 *   everything else   -> static assets from ./ (env.ASSETS)
 */

const WA_NUMBER = "971569028087";
const DEFAULT_PREFILL = "Hi, I want help choosing an Etisalat postpaid plan from postpaidplans.com.";
const CANONICAL_HOST = "postpaidplans.com";

// Collapse http://, www., and any non-apex host to the one canonical origin
// (https://postpaidplans.com) with a 301. GSC 2026-06-08 showed http:// and
// www. variants indexed separately, splitting the homepage's ranking signal
// (https apex was stuck at pos ~24 while http ranked pos ~8). Behind Cloudflare
// the original scheme is read from the CF-Visitor header, not url.protocol.
function canonicalRedirect(request, url) {
  const cfVisitor = request.headers.get("CF-Visitor") || "";
  const isHttp = url.protocol === "http:" || cfVisitor.includes('"scheme":"http"');
  const isNonApex = url.hostname !== CANONICAL_HOST;
  if (!isHttp && !isNonApex) return null;
  return Response.redirect(`https://${CANONICAL_HOST}${url.pathname}${url.search}`, 301);
}

function handleWhatsAppRedirect(request) {
  const url = new URL(request.url);
  const text = url.searchParams.get("text") || DEFAULT_PREFILL;
  const target = `https://wa.me/${WA_NUMBER}?text=${encodeURIComponent(text)}`;
  return Response.redirect(target, 302);
}

// The 3,680 per-number pages (/numbers/etisalat-<digits>/ + the /numbers/ hub) were REMOVED
// 2026-08-09 (owner directive). Rationale: the same mass-generated per-number page pattern drew a
// penalty on the sister site goldennummbers, and on PPP the tree never earned a click (GSC 3 mo to
// 2026-08-09: per-number pages ~2-3 impressions each, 0 clicks) while contributing 425 of the 640
// "not indexed" URLs. 410 (not 404) is deliberate: it is the explicit "intentionally removed"
// signal, so Google de-indexes faster and stops recrawling sooner than it would for a soft 404.
// Keep this rule permanently — deleting it would let these URLs fall back to plain 404s.
function isRemovedNumberPage(url) {
  return url.pathname === "/numbers" || url.pathname.startsWith("/numbers/");
}

// Parent paths Google crawls that have no index page of their own → 301 to a real page so they
// leave GSC "Not found (404)" and pass crawl equity. /ar/blog/ holds AR posts but has no hub index.
function legacyPathRedirect(url) {
  // /ar/blog/ is now a real hub page. Send the slash-less variant to it (the trailing-slash
  // version is served directly by static assets — matching "/ar/blog" only avoids a redirect loop).
  if (url.pathname === "/ar/blog") return `https://${CANONICAL_HOST}/ar/blog/`;
  return null;
}

// ── MAINTENANCE MODE ───────────────────────────────────────────────────────
// Paused 2026-08-17 on the owner's instruction while the brands are reworked.
// UNPAUSED 2026-08-30 on the owner's instruction — inventory is back on the
// re-issued master sheet (1duUVd…), same day goldennummbers.com came back.
// TO PAUSE AGAIN: set MAINTENANCE = true, then `npx wrangler deploy`
// from a clean checkout of main (this repo has no deploy workflow — the live
// site is published manually with wrangler).
//
// 503 + Retry-After is Google's documented signal for planned downtime: the
// URLs stay indexed and crawling is retried later. A 404/410 would instead
// tell Google the pages are gone. Deliberately NO "x-robots-tag: noindex"
// here — that would de-index the very pages the 503 is protecting. Note this
// gate runs BEFORE canonicalRedirect() and the /numbers/ 410 rule, so while
// it is on, every path answers 503 (including the removed-number-page 410s).
const MAINTENANCE = false;
const MAINTENANCE_RETRY_AFTER = 86400; // seconds (24h)

function maintenanceResponse() {
  const html = [
    '<!doctype html><html lang="en"><head><meta charset="utf-8">',
    '<meta name="viewport" content="width=device-width,initial-scale=1">',
    '<title>Postpaid Plans — back shortly</title>',
    '<style>',
    ':root{color-scheme:light dark}',
    '*{box-sizing:border-box}',
    'body{margin:0;min-height:100vh;display:grid;place-items:center;padding:24px;',
    'font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;',
    'background:#0d1117;color:#e6edf3}',
    '.card{max-width:520px;text-align:center}',
    'h1{font-size:clamp(22px,4vw,30px);margin:0 0 12px;letter-spacing:-.01em}',
    'p{margin:0;color:#9aa7b4}',
    '.sub{margin-top:26px;font-size:13px;color:#6b7683}',
    '</style></head><body><div class="card">',
    '<h1>We&rsquo;re temporarily offline for updates</h1>',
    '<p>PostpaidPlans is being updated and will be back shortly.</p>',
    '<div class="sub">Thank you for your patience.</div>',
    '</div></body></html>',
  ].join("");
  return new Response(html, {
    status: 503,
    headers: {
      "content-type": "text/html; charset=utf-8",
      "retry-after": String(MAINTENANCE_RETRY_AFTER),
      "cache-control": "no-store",
    },
  });
}

export default {
  async fetch(request, env) {
    if (MAINTENANCE) return maintenanceResponse();

    const url = new URL(request.url);

    const canonical = canonicalRedirect(request, url);
    if (canonical) return canonical;

    if (isRemovedNumberPage(url)) {
      return new Response("Gone", {
        status: 410,
        headers: {
          "content-type": "text/plain; charset=utf-8",
          "x-robots-tag": "noindex",
          "cache-control": "public, max-age=86400",
        },
      });
    }

    const legacy = legacyPathRedirect(url);
    if (legacy) return Response.redirect(legacy, 301);

    if (url.pathname === "/r") {
      return handleWhatsAppRedirect(request);
    }

    // Fall through to static assets for everything else.
    return env.ASSETS.fetch(request);
  },
};
