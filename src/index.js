/* ==========================================================================
   Worker entry point for iazzus.com.

   Almost every request is a static file and never reaches this code: the
   assets layer serves public/ directly. The one exception is the contact
   endpoint, which is declared in wrangler.toml under assets.run_worker_first
   so it always lands here rather than 404ing against the file system.

   Mail goes out through Cloudflare's own Email Service binding. Sending to
   a verified destination address on your own account is free on every plan
   and does not touch a quota, so there is no third party in the path, no
   API key to leak, and nothing to renew. Setup steps are in the README
   under "Contact form".
   ========================================================================== */

const CONTACT_PATH = "/api/contact";

/* Caps. A contact form has no business receiving more than this, and an
   unbounded body is a free denial-of-wallet vector. */
const MAX_BODY_BYTES = 16 * 1024;
const LIMITS = {
  name: 100,
  email: 254, // RFC 5321 maximum for a full address
  category: 40,
  subject: 200,
  message: 5000,
};

const CATEGORIES = {
  "it-consulting": "IT / Consulting",
  coaching: "Coaching",
  bodybuilding: "Bodybuilding",
  motorcycle: "Motorcycle",
  general: "General",
  other: "Other",
};

/* Deliberately stricter than the spec allows. Anything this rejects is
   something I could not reply to anyway. */
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === CONTACT_PATH) {
      return handleContact(request, env, url);
    }

    // Everything else is a static file.
    return env.ASSETS.fetch(request);
  },
};

/* --------------------------------------------------------------------------
   Contact endpoint
   -------------------------------------------------------------------------- */

async function handleContact(request, env, url) {
  // The form posts to itself; nothing else has any business here. Rejecting
  // foreign origins stops the endpoint being used as a spam relay from
  // somebody else's page.
  const origin = request.headers.get("Origin");
  if (origin && new URL(origin).host !== url.host) {
    return fail(request, 403, "This form only accepts submissions from iazzus.com.");
  }

  if (request.method !== "POST") {
    return fail(request, 405, "Send this form with POST.", { Allow: "POST" });
  }

  const contentType = request.headers.get("Content-Type") || "";
  // JSON means the page's own fetch. Form encoding means the browser
  // submitted it natively, which is what happens with JavaScript blocked.
  const wantsJson = contentType.includes("application/json");

  const declared = Number(request.headers.get("Content-Length") || 0);
  if (declared > MAX_BODY_BYTES) {
    return fail(request, 413, "That message is too long to send.");
  }

  let fields;
  try {
    fields = wantsJson ? await readJson(request) : await readForm(request);
  } catch (error) {
    return fail(request, 400, "That submission could not be read.");
  }
  if (!fields) {
    return fail(request, 413, "That message is too long to send.");
  }

  // Honeypot. Report success so the bot stops retrying, and send nothing.
  if (text(fields.company)) {
    return succeed(request);
  }

  const name = clean(fields.name, LIMITS.name);
  const email = clean(fields.email, LIMITS.email);
  const category = clean(fields.category, LIMITS.category);
  const subject = clean(fields.subject, LIMITS.subject);
  const message = String(fields.message || "").trim().slice(0, LIMITS.message);

  const problems = [];
  if (name.length < 2) problems.push("a name");
  if (!EMAIL_PATTERN.test(email)) problems.push("a valid email address");
  if (!Object.prototype.hasOwnProperty.call(CATEGORIES, category)) {
    problems.push("a category");
  }
  if (subject.length < 3) problems.push("a subject");
  if (message.length < 20) problems.push("a message of at least 20 characters");

  if (problems.length) {
    return fail(request, 400, "Please include " + list(problems) + ".");
  }

  if (!env.EMAIL) {
    // Configuration is missing rather than the visitor doing anything wrong.
    // Say so, and hand them an address that definitely works.
    return fail(
      request,
      503,
      "Message delivery is not configured on the server right now. " +
        "Please email " + (env.CONTACT_TO || "ian.vulovic@live.com") + " instead."
    );
  }

  const label = CATEGORIES[category];

  try {
    await env.EMAIL.send({
      to: env.CONTACT_TO,
      from: { email: env.CONTACT_FROM, name: "IAZZUS contact form" },
      // Replying in a mail client should reach the visitor, not the form.
      replyTo: { email, name },
      subject: `[${label}] ${subject}`,
      text: plainBody({ name, email, label, subject, message, request }),
      html: htmlBody({ name, email, label, subject, message, request }),
    });
  } catch (error) {
    console.error("contact send failed", error && error.code, error && error.message);
    return fail(
      request,
      502,
      "The message could not be sent. Please email " +
        (env.CONTACT_TO || "ian.vulovic@live.com") + " directly."
    );
  }

  return succeed(request);
}

/* --------------------------------------------------------------------------
   Reading the body

   Both readers stop at MAX_BODY_BYTES rather than trusting Content-Length,
   which a client is free to lie about.
   -------------------------------------------------------------------------- */

async function readBounded(request) {
  const buffer = await request.arrayBuffer();
  if (buffer.byteLength > MAX_BODY_BYTES) return null;
  return new TextDecoder().decode(buffer);
}

async function readJson(request) {
  const body = await readBounded(request);
  if (body === null) return null;
  const parsed = JSON.parse(body);
  if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
    throw new Error("not an object");
  }
  return parsed;
}

async function readForm(request) {
  const body = await readBounded(request);
  if (body === null) return null;
  const params = new URLSearchParams(body);
  const out = {};
  params.forEach((value, key) => {
    out[key] = value;
  });
  return out;
}

/* --------------------------------------------------------------------------
   Helpers
   -------------------------------------------------------------------------- */

function text(value) {
  return String(value == null ? "" : value).trim();
}

/* Single-line fields get their line breaks stripped before they are used.
   The Email Service builds the MIME itself, but a stray newline in a
   subject is a header-injection shape and there is no reason to allow it. */
function clean(value, max) {
  return text(value).replace(/[\r\n]+/g, " ").slice(0, max).trim();
}

function list(items) {
  if (items.length === 1) return items[0];
  return items.slice(0, -1).join(", ") + " and " + items[items.length - 1];
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function metaLines(request) {
  const cf = request.cf || {};
  const country = cf.country || "unknown";
  return ["Country: " + country, "Received: " + new Date().toISOString()];
}

function plainBody({ name, email, label, subject, message, request }) {
  return [
    "From:     " + name + " <" + email + ">",
    "Category: " + label,
    "Subject:  " + subject,
    "",
    message,
    "",
    "---",
    ...metaLines(request),
    "Sent from the contact form on iazzus.com",
  ].join("\n");
}

function htmlBody({ name, email, label, subject, message, request }) {
  const rows = [
    ["From", escapeHtml(name) + " &lt;" + escapeHtml(email) + "&gt;"],
    ["Category", escapeHtml(label)],
    ["Subject", escapeHtml(subject)],
  ]
    .map(
      ([key, value]) =>
        "<tr><td style=\"padding:2px 12px 2px 0;color:#666\">" +
        key +
        "</td><td style=\"padding:2px 0\">" +
        value +
        "</td></tr>"
    )
    .join("");

  return [
    '<div style="font-family:system-ui,sans-serif;font-size:15px;line-height:1.6">',
    "<table>" + rows + "</table>",
    "<hr style=\"border:0;border-top:1px solid #ddd;margin:16px 0\">",
    "<div>" + escapeHtml(message).replace(/\n/g, "<br>") + "</div>",
    "<hr style=\"border:0;border-top:1px solid #ddd;margin:16px 0\">",
    '<p style="color:#666;font-size:13px">' +
      metaLines(request).map(escapeHtml).join("<br>") +
      "<br>Sent from the contact form on iazzus.com</p>",
    "</div>",
  ].join("");
}

/* --------------------------------------------------------------------------
   Responses

   A fetch submission gets JSON. A native form submission gets a real page,
   because without JavaScript there is nothing on the other end to render a
   message.
   -------------------------------------------------------------------------- */

function prefersJson(request) {
  const contentType = request.headers.get("Content-Type") || "";
  if (contentType.includes("application/json")) return true;
  const accept = request.headers.get("Accept") || "";
  return accept.includes("application/json") && !accept.includes("text/html");
}

const NO_STORE = {
  "Cache-Control": "no-store",
  "Referrer-Policy": "strict-origin-when-cross-origin",
  "X-Content-Type-Options": "nosniff",
};

function succeed(request) {
  if (prefersJson(request)) {
    return Response.json({ ok: true }, { headers: NO_STORE });
  }
  return page(
    200,
    "Message sent",
    "Thanks. Your message is on its way and I will reply to the address you gave."
  );
}

function fail(request, status, detail, extraHeaders) {
  if (prefersJson(request)) {
    return Response.json(
      { ok: false, error: detail },
      { status, headers: { ...NO_STORE, ...extraHeaders } }
    );
  }
  return page(status, "Message not sent", detail, extraHeaders);
}

/* Matches the site's own styling by loading the same stylesheets, so the
   no-JavaScript path does not dump the visitor onto a bare white page. */
function page(status, heading, body, extraHeaders) {
  const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${escapeHtml(heading)} | IAZZUS</title>
<meta name="robots" content="noindex">
<link rel="icon" href="/favicon-32.png" type="image/png" sizes="32x32">
<link rel="stylesheet" href="/assets/css/reset.css">
<link rel="stylesheet" href="/assets/css/variables.css">
<link rel="stylesheet" href="/assets/css/global.css">
<link rel="stylesheet" href="/assets/css/components.css">
<link rel="stylesheet" href="/assets/css/responsive.css">
<link rel="stylesheet" href="/assets/css/noscript.css">
</head>
<body>
<main class="section">
  <div class="container container--narrow stack stack--md">
    <a class="wordmark" href="/">IAZZUS</a>
    <h1>${escapeHtml(heading)}</h1>
    <p class="lead">${escapeHtml(body)}</p>
    <p><a class="btn btn--secondary" href="/contact/">Back to contact</a></p>
  </div>
</main>
</body>
</html>`;

  return new Response(html, {
    status,
    headers: {
      "Content-Type": "text/html; charset=utf-8",
      ...NO_STORE,
      ...extraHeaders,
    },
  });
}
