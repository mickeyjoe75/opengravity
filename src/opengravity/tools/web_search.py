import httpx
import re
import urllib.parse
from opengravity.tools.registry import tool

@tool(description="Search the web using DuckDuckGo and return results with titles, URLs, and snippets")
def web_search(query: str, num_results: int = 5) -> str:
    """Search the web."""
    try:
        url = "https://html.duckduckgo.com/html/"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        data = {'q': query}
        
        with httpx.Client() as client:
            response = client.post(url, data=data, headers=headers)
            response.raise_for_status()
            html = response.text
            
        results = []
        # Find all result blocks using regex on the raw HTML
        blocks = re.findall(r'<a class="result__url" href="([^"]+)".*?<h2 class="result__title">.*?<a[^>]*>(.*?)</a>.*?<a class="result__snippet[^>]*>(.*?)</a>', html, re.DOTALL)
        
        for i, (res_url, title, snippet) in enumerate(blocks):
            if i >= num_results:
                break
                
            clean_title = re.sub(r'<[^>]+>', '', title).strip()
            clean_snippet = re.sub(r'<[^>]+>', '', snippet).strip()
            
            clean_title = clean_title.replace('&#x27;', "'").replace('&quot;', '"')
            clean_snippet = clean_snippet.replace('&#x27;', "'").replace('&quot;', '"')
            
            parsed_url = res_url
            if 'uddg=' in res_url:
                try:
                    parsed_url = urllib.parse.unquote(res_url.split('uddg=')[1].split('&')[0])
                except Exception:
                    pass
            
            results.append(f"Result {i+1}:\nTitle: {clean_title}\nURL: {parsed_url}\nSnippet: {clean_snippet}\n")
            
        if not results:
            return "No results found."
            
        return "\n".join(results)
        
    except Exception as e:
        return f"Error performing web search: {e}"
