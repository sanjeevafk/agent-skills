#!/usr/bin/env python3
"""
Crawl4AI / Ottomator Web Crawler Helper Script
"""

import argparse
import asyncio
import sys

def main():
    parser = argparse.ArgumentParser(description="Ottomator Crawl4AI Web Crawler")
    parser.add_argument("--url", help="Target URL to scrape or crawl")
    parser.add_argument("--sitemap", help="Sitemap XML URL for parallel crawling")
    parser.add_argument("--recursive", action="store_true", help="Crawl internal links recursively")
    parser.add_argument("--max-depth", type=int, default=2, help="Maximum recursion depth (default: 2)")
    parser.add_argument("--max-concurrent", type=int, default=5, help="Max concurrent requests")
    parser.add_argument("--chunk", action="store_true", help="Chunk output Markdown by headers")
    parser.add_argument("--output", help="Output file path (default: stdout)")

    args = parser.parse_args()

    if not args.url and not args.sitemap:
        parser.error("Must specify either --url or --sitemap")

    try:
        from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
    except ImportError:
        print("Crawl4AI not installed. Install via: pip install crawl4ai && crawl4ai-setup", file=sys.stderr)
        sys.exit(1)

    async def run():
        async with AsyncWebCrawler() as crawler:
            target = args.url or args.sitemap
            print(f"[*] Crawling {target}...", file=sys.stderr)
            result = await crawler.arun(url=target)
            if result.success:
                content = result.markdown
                if args.output:
                    with open(args.output, "w") as f:
                        f.write(content)
                    print(f"[+] Saved output to {args.output}", file=sys.stderr)
                else:
                    print(content)
            else:
                print(f"[-] Crawl failed: {result.error_message}", file=sys.stderr)

    asyncio.run(run())

if __name__ == "__main__":
    main()
