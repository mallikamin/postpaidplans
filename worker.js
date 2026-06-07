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

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    const canonical = canonicalRedirect(request, url);
    if (canonical) return canonical;

    if (url.pathname === "/r") {
      return handleWhatsAppRedirect(request);
    }

    // Fall through to static assets for everything else.
    return env.ASSETS.fetch(request);
  },
};
