#!/usr/bin/env python3
"""
Exa API wrapper for Crypt Librarian film discovery.

Provides direct API access to all Exa endpoints:
- search: Find film lists, articles, recommendations
- contents: Extract full content from URLs (Letterboxd lists, Criterion essays)
- find_similar: Discover films similar to a reference
- research: Deep research with AI synthesis and citations

Usage:
    python exa_film_search.py search "gothic horror films pre-2010"
    python exa_film_search.py contents "https://letterboxd.com/user/list/gothic-films/"
    python exa_film_search.py similar "https://letterboxd.com/film/eyes-wide-shut/"
    python exa_film_search.py research "occult ritual films similar to Eyes Wide Shut"

Requires: EXA_API_KEY environment variable
Install: pip install requests
"""

import os
import sys
import json
import argparse
import requests
from typing import Optional, List, Dict, Any

EXA_API_KEY = os.environ.get("EXA_API_KEY")
BASE_URL = "https://api.exa.ai"

def _headers() -> Dict[str, str]:
    if not EXA_API_KEY:
        raise ValueError("EXA_API_KEY environment variable not set")
    return {
        "Content-Type": "application/json",
        "x-api-key": EXA_API_KEY
    }

def search(
    query: str,
    num_results: int = 10,
    include_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    include_text: bool = True
) -> Dict[str, Any]:
    """
    Search the web using Exa's neural search.

    Args:
        query: Natural language search query (be descriptive!)
        num_results: Number of results to return (default: 10)
        include_domains: Only search these domains (e.g., ["letterboxd.com", "criterion.com"])
        exclude_domains: Exclude these domains from results
        start_date: Filter results after this date (YYYY-MM-DD)
        end_date: Filter results before this date (YYYY-MM-DD)
        include_text: Include full text content in results

    Returns:
        Dict with 'results' list containing title, url, text, publishedDate
    """
    payload = {
        "query": query,
        "numResults": num_results,
        "contents": {
            "text": include_text
        }
    }

    if include_domains:
        payload["includeDomains"] = include_domains
    if exclude_domains:
        payload["excludeDomains"] = exclude_domains
    if start_date:
        payload["startPublishedDate"] = start_date
    if end_date:
        payload["endPublishedDate"] = end_date

    response = requests.post(
        f"{BASE_URL}/search",
        headers=_headers(),
        json=payload
    )
    response.raise_for_status()
    return response.json()

def get_contents(urls: List[str]) -> Dict[str, Any]:
    """
    Get clean, parsed content from specific URLs.

    This is the "crawling" function - extracts full text from known URLs.

    Args:
        urls: List of URLs to extract content from

    Returns:
        Dict with 'results' list containing url, title, text
    """
    payload = {
        "ids": urls,
        "text": True
    }

    response = requests.post(
        f"{BASE_URL}/contents",
        headers=_headers(),
        json=payload
    )
    response.raise_for_status()
    return response.json()

def find_similar(
    url: str,
    num_results: int = 10,
    include_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Find pages similar to a given URL.

    Great for finding films similar to a reference film's Letterboxd/IMDB page.

    Args:
        url: Reference URL to find similar pages for
        num_results: Number of similar results to return
        include_domains: Only include results from these domains
        exclude_domains: Exclude results from these domains

    Returns:
        Dict with 'results' list of similar pages
    """
    payload = {
        "url": url,
        "numResults": num_results,
        "contents": {
            "text": True
        }
    }

    if include_domains:
        payload["includeDomains"] = include_domains
    if exclude_domains:
        payload["excludeDomains"] = exclude_domains

    response = requests.post(
        f"{BASE_URL}/findSimilar",
        headers=_headers(),
        json=payload
    )
    response.raise_for_status()
    return response.json()

def research(query: str) -> str:
    """
    Deep research with AI synthesis and citations.

    Uses Exa's /answer endpoint for complex queries requiring
    multi-source synthesis. Returns a comprehensive answer with citations.

    Args:
        query: Research question or topic

    Returns:
        Synthesized answer with citations
    """
    payload = {
        "query": query,
        "text": True
    }

    response = requests.post(
        f"{BASE_URL}/answer",
        headers=_headers(),
        json=payload
    )
    response.raise_for_status()
    result = response.json()

    # Extract the answer
    if "answer" in result:
        return result["answer"]
    return json.dumps(result, indent=2)

def format_results(results: Dict[str, Any], max_text_length: int = 500) -> str:
    """Format search results for display."""
    output = []

    if "results" in results:
        for i, r in enumerate(results["results"], 1):
            output.append(f"\n{'='*60}")
            output.append(f"[{i}] {r.get('title', 'No title')}")
            output.append(f"    URL: {r.get('url', 'No URL')}")
            if r.get('publishedDate'):
                output.append(f"    Date: {r['publishedDate'][:10]}")
            if r.get('text'):
                text = r['text'][:max_text_length]
                if len(r['text']) > max_text_length:
                    text += "..."
                output.append(f"    Text: {text}")

    return "\n".join(output)

def main():
    parser = argparse.ArgumentParser(
        description="Exa API wrapper for Crypt Librarian film discovery"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search the web")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("-n", "--num", type=int, default=10, help="Number of results")
    search_parser.add_argument("--domains", nargs="+", help="Only search these domains")
    search_parser.add_argument("--exclude", nargs="+", help="Exclude these domains")
    search_parser.add_argument("--json", action="store_true", help="Output raw JSON")

    # Contents command
    contents_parser = subparsers.add_parser("contents", help="Get content from URLs")
    contents_parser.add_argument("urls", nargs="+", help="URLs to extract content from")
    contents_parser.add_argument("--json", action="store_true", help="Output raw JSON")

    # Similar command
    similar_parser = subparsers.add_parser("similar", help="Find similar pages")
    similar_parser.add_argument("url", help="Reference URL")
    similar_parser.add_argument("-n", "--num", type=int, default=10, help="Number of results")
    similar_parser.add_argument("--domains", nargs="+", help="Only include these domains")
    similar_parser.add_argument("--json", action="store_true", help="Output raw JSON")

    # Research command
    research_parser = subparsers.add_parser("research", help="Deep research with AI")
    research_parser.add_argument("query", help="Research question")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "search":
            results = search(
                args.query,
                num_results=args.num,
                include_domains=args.domains,
                exclude_domains=args.exclude
            )
            if args.json:
                print(json.dumps(results, indent=2))
            else:
                print(format_results(results))

        elif args.command == "contents":
            results = get_contents(args.urls)
            if args.json:
                print(json.dumps(results, indent=2))
            else:
                print(format_results(results, max_text_length=2000))

        elif args.command == "similar":
            results = find_similar(
                args.url,
                num_results=args.num,
                include_domains=args.domains
            )
            if args.json:
                print(json.dumps(results, indent=2))
            else:
                print(format_results(results))

        elif args.command == "research":
            answer = research(args.query)
            print(answer)

    except requests.exceptions.HTTPError as e:
        print(f"API Error: {e}", file=sys.stderr)
        if e.response is not None:
            print(f"Response: {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
