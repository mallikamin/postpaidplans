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

function handleWhatsAppRedirect(request) {
  const url = new URL(request.url);
  const text = url.searchParams.get("text") || DEFAULT_PREFILL;
  const target = `https://wa.me/${WA_NUMBER}?text=${encodeURIComponent(text)}`;
  return Response.redirect(target, 302);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === "/r") {
      return handleWhatsAppRedirect(request);
    }

    // Fall through to static assets for everything else.
    return env.ASSETS.fetch(request);
  },
};
