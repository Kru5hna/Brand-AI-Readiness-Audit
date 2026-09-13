# AI Quotability, RAG Friendliness & Freshness Heuristics

## 1. The Inverted Pyramid for AI Quotability
AI assistants (like ChatGPT, Claude, and Perplexity) rely on neural embeddings and RAG chunking algorithms that slice web pages into 200–500 token windows.
- If a brand's core value proposition and technical identity are buried at the bottom of the page, or scattered across marketing buzzwords ("revolutionizing digital paradigms"), the RAG retriever assigns a low semantic similarity score.
- **Rule**: The first 150 words of a page must state **who**, **what**, **how**, and **key differentiator** in plain, declarative syntax ("Acme is an open-source database engine built for sub-millisecond vector search").

## 2. Information Density vs. Boilerplate Clutter
Scraping tools like Readability or Trafilatura strip out `<nav>`, `<header>`, and `<footer>` elements before passing text to the LLM.
- If content has a low density ratio (e.g., 80% cookie notices, navigation menus, and testimonials, and only 20% factual text), the extraction algorithm may deem the page low quality and drop it.
- **Rule**: Keep content-to-boilerplate ratio >= 35%. Use semantic HTML (`<main>`, `<article>`) to delineate substantive text.

## 3. Freshness & Temporal Signals
AI models have built-in recency heuristics to avoid citing obsolete information.
- Outdated copyright years (e.g. copyright 2022-2024 when audited in 2026) signal an abandoned project.
- Missing `article:modified_time` or schema `dateModified` weakens citation confidence for technical or price-sensitive topics.
- **Rule**: Keep copyright current and emit explicit ISO 8601 update timestamps in metadata.
