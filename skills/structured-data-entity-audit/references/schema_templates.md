# Schema.org Structured Data Templates for AI Discoverability

## 1. Organization & Entity Disambiguation (`Organization` / `Corporation`)
Place on the homepage to establish machine-readable brand identity and authoritative grounding:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Acme Software Inc.",
  "alternateName": "AcmeAI",
  "url": "https://example.com",
  "logo": "https://example.com/assets/logo.png",
  "description": "Acme provides automated data pipeline orchestration for enterprise cloud platforms.",
  "sameAs": [
    "https://www.wikidata.org/wiki/Q12345678",
    "https://en.wikipedia.org/wiki/Acme_Corporation",
    "https://www.linkedin.com/company/acme",
    "https://www.crunchbase.com/organization/acme",
    "https://twitter.com/acme"
  ],
  "contactPoint": {
    "@type": "ContactPoint",
    "telephone": "+1-800-555-0199",
    "contactType": "customer service",
    "availableLanguage": "English"
  }
}
</script>
```

## 2. Product & Offer Schema (`Product` / `SoftwareApplication`)
Enables AI assistants to quote accurate specs, licensing, and pricing:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "Acme Cloud Orchestrator",
  "operatingSystem": "Linux, Windows, macOS",
  "applicationCategory": "DeveloperApplication",
  "description": "Autonomous cloud pipeline infrastructure management with instant disaster recovery.",
  "offers": {
    "@type": "Offer",
    "price": "49.00",
    "priceCurrency": "USD",
    "priceValidUntil": "2027-01-01",
    "availability": "https://schema.org/InStock"
  }
}
</script>
```

## 3. FAQ Schema (`FAQPage`)
Enables direct question-and-answer extraction for conversational assistants:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{
    "@type": "Question",
    "name": "What integrations are supported?",
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "Acme supports native integrations with AWS, Azure, Google Cloud Platform, and Kubernetes."
    }
  }]
}
</script>
```
