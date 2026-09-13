"""
Automated Test Suite for Brand AI-Readiness Marketplace
Tests deterministic detection across mock scenarios:
- CSR Hydration Shells
- AI Bot Blocking in robots.txt
- Meta Noindex / Nosnippet
- Missing Schema.org & Non-Text Lock
- Deep-Link Orientation & Breadcrumbs
- Pristine AI-Ready Site (False Positive Baseline)
"""

import http.server
import json
import os
import socketserver
import sys
import threading
import time
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import importlib

orchestrate = importlib.import_module("skills.audit-orchestrator.scripts.orchestrate")
reporter = importlib.import_module("skills.audit-orchestrator.scripts.reporter")



class MockSiteHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress console logging during test runs

    def do_GET(self):
        path = self.path.split("?")[0]

        # Scenario 1: robots.txt with AI blocks
        if path == "/robots.txt":
            content = "User-agent: GPTBot\nDisallow: /\nUser-agent: ClaudeBot\nDisallow: /\n"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))
            return

        # Scenario 2: CSR Hydration Wall page
        if path == "/csr-site/":
            content = """<!DOCTYPE html>
            <html>
            <head><title>Modern React App</title></head>
            <body>
              <div id="root"></div>
              <script src="/bundle1.js"></script>
              <script src="/bundle2.js"></script>
            </body>
            </html>"""
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))
            return

        # Scenario 3: Meta Noindex & Missing Schema
        if path == "/noindex-site/":
            content = """<!DOCTYPE html>
            <html>
            <head>
              <title>Confidential Portal</title>
              <meta name="robots" content="noindex, nosnippet">
            </head>
            <body>
              <p>Welcome to our internal portal.</p>
              <img src="/chart.png">
            </body>
            </html>"""
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))
            return

        # Scenario 4: Deep page without breadcrumbs & unclear hero
        if path == "/features/cloud-audit":
            content = """<!DOCTYPE html>
            <html>
            <head><title>Cloud Audit Feature</title></head>
            <body>
              <h2>Feature Highlights</h2>
              <p>Explore features.</p>
            </body>
            </html>"""
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))
            return

        # Scenario 5: Optimized AI-Ready Page
        if path == "/optimized/":
            content = """<!DOCTYPE html>
            <html>
            <head>
              <title>AcmeAI — Enterprise Cloud Observability</title>
              <script type="application/ld+json">
              {
                "@context": "https://schema.org",
                "@type": "Organization",
                "name": "AcmeAI",
                "url": "https://acme.ai",
                "sameAs": ["https://www.wikidata.org/wiki/Q12345"]
              }
              </script>
            </head>
            <body>
              <header class="hero">
                <h1>AcmeAI Cloud Observability</h1>
                <p class="hero-subhead">AcmeAI is an automated observability platform that delivers sub-second telemetry analysis for distributed Kubernetes clusters.</p>
                <a href="/signup" class="btn btn-primary">Start Free Trial</a>
              </header>
              <main>
                <article>
                  <h2>Instant Log Correlation</h2>
                  <p>Correlate system events across multi-cloud deployments seamlessly.</p>
                  <img src="/arch.png" alt="Architecture diagram depicting telemetry flow from Kubernetes to AcmeAI ingest engine">
                </article>
              </main>
              <footer>
                <p>&copy; 2026 AcmeAI, Inc. All rights reserved.</p>
              </footer>
            </body>
            </html>"""
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))
            return

        # Default 404
        self.send_response(404)
        self.end_headers()


class MarketplaceE2ETest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = socketserver.TCPServer(("127.0.0.1", 0), MockSiteHandler)
        cls.port = cls.server.server_address[1]
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_schema_conformance(self):
        """Verify that audit report output strictly conforms to the contest schema."""
        report = orchestrate.run_orchestrated_audit(f"{self.base_url}/optimized/")
        errors = reporter.validate_report_schema(report)
        self.assertEqual(len(errors), 0, f"Schema validation failed: {errors}")
        self.assertIn("site", report)
        self.assertIn("audited_at", report)
        self.assertIn("summary", report)
        self.assertIn("findings", report)
        self.assertIn("total_findings", report["summary"])
        self.assertIn("critical", report["summary"])
        self.assertIn("high", report["summary"])
        self.assertIn("medium", report["summary"])

    def test_csr_hydration_detection(self):
        """Verify that client-side hydration shells trigger F-CRAWL-CSR-HYDRATION-WALL."""
        report = orchestrate.run_orchestrated_audit(f"{self.base_url}/csr-site/")
        finding_ids = [f["id"] for f in report["findings"]]
        self.assertIn("F-CRAWL-CSR-HYDRATION-WALL", finding_ids)
        finding = next(f for f in report["findings"] if f["id"] == "F-CRAWL-CSR-HYDRATION-WALL")
        self.assertEqual(finding["severity"], "high")
        self.assertIn("suggested_action", finding)
        self.assertIn("summary", finding["suggested_action"])

    def test_ai_bots_blocked_detection(self):
        """Verify that blocking AI user agents triggers F-CRAWL-AI-BOTS-BLOCKED."""
        report = orchestrate.run_orchestrated_audit(f"{self.base_url}/blocked-bot/")
        finding_ids = [f["id"] for f in report["findings"]]
        self.assertIn("F-CRAWL-AI-BOTS-BLOCKED", finding_ids)

    def test_meta_noindex_detection(self):
        """Verify that meta robots noindex triggers F-CRAWL-META-NOINDEX."""
        report = orchestrate.run_orchestrated_audit(f"{self.base_url}/noindex-site/")
        finding_ids = [f["id"] for f in report["findings"]]
        self.assertIn("F-CRAWL-META-NOINDEX", finding_ids)

    def test_deep_page_missing_breadcrumbs(self):
        """Verify that landing on deep links without breadcrumbs triggers F-ENG-DEEP-NO-BREADCRUMBS."""
        report = orchestrate.run_orchestrated_audit(f"{self.base_url}/features/cloud-audit")
        finding_ids = [f["id"] for f in report["findings"]]
        self.assertIn("F-ENG-DEEP-NO-BREADCRUMBS", finding_ids)

    def test_optimized_site_high_scores(self):
        """Verify that an optimized site scores high with 0 critical findings."""
        report = orchestrate.run_orchestrated_audit(f"{self.base_url}/optimized/")
        self.assertEqual(report["summary"]["critical"], 0)
        finding_ids = [f["id"] for f in report["findings"]]
        # Shouldn't trigger CSR, shouldn't trigger missing alt, shouldn't trigger unclear hero
        self.assertNotIn("F-CRAWL-CSR-HYDRATION-WALL", finding_ids)
        self.assertNotIn("F-ENG-HERO-UNCLEAR", finding_ids)
        self.assertNotIn("F-DATA-NONTEXT-ALT-MISSING", finding_ids)


if __name__ == "__main__":
    unittest.main()
