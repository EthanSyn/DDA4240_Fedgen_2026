"""
FedGen Data Backend - Lightweight HTTP server serving sample datasets
and proxying real-world API data for the FedGen dataspace.

Routes:
  /legal/documents  - Local legal corpus sample
  /news/articles    - Local news corpus sample
  /legal/live       - Live academic/legal data from OpenAlex API
  /news/live        - Live tech news from HackerNews API
  /health           - Health check
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import time
import urllib.request
import urllib.error
import urllib.parse

DATA_DIR = os.environ.get("DATA_DIR", "/data")
PORT = int(os.environ.get("PORT", "8080"))
CACHE_TTL = 300  # cache live API responses for 5 minutes

# Simple in-memory cache: {key: (timestamp, data)}
_cache = {}

def _cached_fetch(key, url, transform_fn, fallback_file=None):
    """Fetch from URL with caching and fallback."""
    now = time.time()
    if key in _cache and now - _cache[key][0] < CACHE_TTL:
        return _cache[key][1]
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "FedGen-DataBackend/1.0"})
        resp = urllib.request.urlopen(req, timeout=15)
        raw = json.loads(resp.read())
        data = transform_fn(raw)
        _cache[key] = (now, data)
        return data
    except Exception as e:
        print(f"[DataBackend] Live API error for {key}: {e}")
        if key in _cache:
            return _cache[key][1]  # stale cache
        if fallback_file:
            path = os.path.join(DATA_DIR, fallback_file)
            if os.path.exists(path):
                with open(path) as f:
                    return json.load(f)
        return {"error": str(e)}


def _transform_openalex(raw):
    """Transform OpenAlex API response into FedGen legal/academic format."""
    docs = []
    for i, work in enumerate(raw.get("results", [])):
        title = work.get("title", "Untitled")
        abstract = ""
        inv_index = work.get("abstract_inverted_index", {})
        if inv_index:
            word_positions = []
            for word, positions in inv_index.items():
                for pos in positions:
                    word_positions.append((pos, word))
            word_positions.sort()
            abstract = " ".join(w for _, w in word_positions)
        concepts = [c.get("display_name", "") for c in work.get("concepts", [])[:3]]
        docs.append({
            "id": f"openalex-{i+1:03d}",
            "title": title,
            "category": concepts[0] if concepts else "general",
            "content": abstract or title,
            "source": "OpenAlex API",
            "year": work.get("publication_year", 0),
            "cited_by": work.get("cited_by_count", 0),
            "doi": work.get("doi", ""),
            "concepts": concepts,
            "license": "Open-Access"
        })
    return {
        "documents": docs,
        "metadata": {
            "total_documents": len(docs),
            "domain": "legal_academic",
            "provider": "Node-A-Legal-Archives",
            "source_api": "OpenAlex (openalex.org)",
            "live": True
        }
    }


def _transform_hackernews_algolia(raw):
    """Transform HN Algolia search API response into FedGen news format."""
    articles = []
    for hit in raw.get("hits", []):
        articles.append({
            "id": f"hn-{hit.get('objectID', '')}",
            "headline": hit.get("title", "Untitled"),
            "category": "technology",
            "content": (hit.get("title", "") + ". " +
                        (hit.get("story_text", "") or hit.get("comment_text", "") or
                         f"Source: {hit.get('url', 'N/A')}")),
            "source": "Hacker News (Algolia API)",
            "published": hit.get("created_at", "")[:10],
            "score": hit.get("points", 0),
            "url": hit.get("url", ""),
            "license": "Public"
        })
    return {
        "articles": articles,
        "metadata": {
            "total_articles": len(articles),
            "domain": "news_media",
            "provider": "Node-B-News-Syndicate",
            "source_api": "Hacker News (hn.algolia.com)",
            "live": True
        }
    }


def _wikidata_sparql_url():
    query = """
PREFIX schema: <http://schema.org/>
SELECT ?item ?itemLabel ?itemDescription WHERE {
  ?item rdfs:label ?itemLabel.
  FILTER(LANG(?itemLabel) = "en")
  VALUES ?itemLabel {
    "artificial intelligence"@en
    "machine learning"@en
    "data privacy"@en
    "data protection"@en
    "General Data Protection Regulation"@en
    "cybersecurity"@en
  }
  OPTIONAL {
    ?item schema:description ?itemDescription.
    FILTER(LANG(?itemDescription) = "en")
  }
}
LIMIT 12
"""
    params = urllib.parse.urlencode({"query": query, "format": "json"})
    return f"https://query.wikidata.org/sparql?{params}"


def _transform_wikidata(raw):
    records = []
    for row in raw.get("results", {}).get("bindings", []):
        uri = row.get("item", {}).get("value", "")
        label = row.get("itemLabel", {}).get("value", "")
        description = row.get("itemDescription", {}).get("value", "")
        entity_id = uri.rstrip("/").split("/")[-1] if uri else ""
        records.append({
            "id": entity_id,
            "label": label,
            "description": description,
            "uri": uri,
            "source": "Wikidata Query Service",
            "database": "Wikidata Knowledge Graph",
            "access_method": "SPARQL API",
            "license": "CC0"
        })
    return {
        "records": records,
        "metadata": {
            "total_records": len(records),
            "domain": "third_party_knowledge_graph",
            "provider": "Node-A-Legal-Archives",
            "source_database": "Wikidata Query Service (SPARQL)",
            "live": True
        }
    }


class DataHandler(BaseHTTPRequestHandler):
    STATIC_ROUTES = {
        "/legal/documents": "legal_sample.json",
        "/news/articles": "news_sample.json",
    }

    def do_GET(self):
        if self.path == "/health":
            self._json_response(200, {"status": "healthy"})
            return

        if self.path == "/":
            catalog = {
                "service": "FedGen Data Backend",
                "datasets": [
                    {"path": "/legal/documents", "description": "Legal corpus (Pile-of-Law sample, static)"},
                    {"path": "/news/articles",   "description": "News corpus (CNN/DailyMail sample, static)"},
                    {"path": "/legal/live",      "description": "Live academic/legal data (OpenAlex API)"},
                    {"path": "/news/live",       "description": "Live tech news (Hacker News API)"},
                    {"path": "/thirdparty/wikidata", "description": "Live third-party knowledge graph data (Wikidata SPARQL)"},
                ]
            }
            self._json_response(200, catalog)
            return

        # Live API routes
        if self.path == "/legal/live":
            data = _cached_fetch(
                "legal_live",
                "https://api.openalex.org/works?search=data+privacy+law&per_page=30&sort=cited_by_count:desc",
                _transform_openalex,
                fallback_file="legal_sample.json"
            )
            self._json_response(200, data)
            return

        if self.path == "/news/live":
            data = _cached_fetch(
                "news_live",
                "https://hn.algolia.com/api/v1/search?query=AI+technology&tags=story&hitsPerPage=20",
                _transform_hackernews_algolia,
                fallback_file="news_sample.json"
            )
            self._json_response(200, data)
            return

        if self.path == "/thirdparty/wikidata":
            data = _cached_fetch(
                "wikidata_kg",
                _wikidata_sparql_url(),
                _transform_wikidata
            )
            self._json_response(200, data)
            return

        # Static file routes
        filename = self.STATIC_ROUTES.get(self.path)
        if filename:
            filepath = os.path.join(DATA_DIR, filename)
            if os.path.exists(filepath):
                with open(filepath) as f:
                    self._json_response(200, json.load(f))
            else:
                self._json_response(404, {"error": f"Data file not found: {filename}"})
        else:
            self._json_response(404, {"error": "Not found"})

    def _json_response(self, code, body):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body, indent=2).encode())

    def log_message(self, format, *args):
        print(f"[DataBackend] {args[0]}")

if __name__ == "__main__":
    print(f"FedGen Data Backend starting on port {PORT}, serving from {DATA_DIR}")
    HTTPServer(("0.0.0.0", PORT), DataHandler).serve_forever()
