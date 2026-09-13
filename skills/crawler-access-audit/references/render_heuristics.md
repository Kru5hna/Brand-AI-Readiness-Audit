# Render Heuristics: Client-Side Rendering (CSR) vs Static SSR Parity

## The AI Crawler Render Gap
Unlike traditional Googlebot, which runs a full two-stage crawling pipeline with headless Chromium rendering (often with a delay), **AI assistant real-time retrieval agents (ChatGPT Search, Claude Search, PerplexityBot) predominantly perform fast HTTP GET fetches** using lightweight HTTP parsers without running JavaScript runtimes.

If a web application relies purely on client-side SPA frameworks (vanilla React, Vue, Angular, or client-only Next/Vite apps) without Server-Side Rendering (SSR) or Static Site Generation (SSG), the HTTP crawler receives only an empty HTML shell:
```html
<div id="root"></div>
<script src="/static/bundle.js"></script>
```

To the AI retrieval bot, the page is completely empty, resulting in zero discoverability and zero citations.

## Detection Heuristics

1. **Text-to-Code Ratio**:
   - Compute stripped visible text word count of the raw HTML payload.
   - If `visible_word_count < 150` and `len(scripts) > 3` or total `<script>` character weight > 70% of total payload, flag as `F-CRAWL-003: CSR Hydration Wall`.

2. **Empty Mounting Container**:
   - Check for classic SPA root mounting elements: `<div id="root">`, `<div id="app">`, `<div id="__next">`.
   - If container has 0 text children or only contains a loading spinner (`<div class="loader">`, "Loading..."), the site lacks SSR content parity.

3. **Noscript Fallbacks**:
   - Check for `<noscript>` elements.
   - If missing, or if `<noscript>` only says "You need to enable JavaScript to run this app", bots without JS engines have zero readable fallback.
