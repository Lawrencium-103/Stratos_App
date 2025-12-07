import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
import google.generativeai as genai
import os
import time
import random
from fake_useragent import UserAgent

def get_stealth_headers():
    """Generates random headers to mimic a real browser."""
    try:
        ua = UserAgent()
        user_agent = ua.random
    except:
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        
    return {
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.google.com/',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

def search_google_news(query, max_results=3):
    """Searches Google News via RSS feed."""
    print(f"  📰 Searching Google News for: {query}...")
    rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    results = []
    try:
        # Google News RSS usually accepts standard requests, but stealth doesn't hurt
        response = requests.get(rss_url, headers=get_stealth_headers(), timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item', limit=max_results)
        
        for item in items:
            title = item.title.text
            link = item.link.text
            results.append({'title': title, 'href': link})
            
    except Exception as e:
        print(f"  ❌ Google News search failed: {e}")
    return results

def search_web(query, max_results=3):
    """Searches DuckDuckGo and Google News for the query."""
    print(f"  🔍 Searching for: {query}...")
    results = []
    
    # 1. Google News RSS (Great for recent news)
    google_results = search_google_news(query, max_results=2)
    results.extend(google_results)

    # 2. DuckDuckGo (Great for general facts)
    try:
        with DDGS() as ddgs:
            ddg_gen = ddgs.text(query, max_results=2)
            for r in ddg_gen:
                results.append(r)
    except Exception as e:
        print(f"  ❌ DuckDuckGo search failed: {e}")
        
    return results

def scrape_content(url):
    """Scrapes the main text content from a URL using stealth headers."""
    print(f"  ⬇️ Scraping (Stealth): {url}...")
    try:
        # Random delay to be polite and avoid some rate limits
        time.sleep(random.uniform(0.5, 1.5))
        
        response = requests.get(url, headers=get_stealth_headers(), timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header", "aside", "iframe"]):
            script.decompose()
            
        text = soup.get_text(separator=' ', strip=True)
        
        # Clean up whitespace
        text = ' '.join(text.split())
        
        # Limit content length
        return text[:3000] + "..." if len(text) > 3000 else text
        
    except Exception as e:
        print(f"  ⚠️ Could not scrape {url}: {e}")
        return ""

def generate_keywords(topic, context, api_key):
    """Uses Gemini to generate SEO keywords."""
    print("  🔑 Generating SEO keywords...")
    genai.configure(api_key=api_key)
    
    prompt = f"""
    Based on the following topic and context, generate a comma-separated list of 10 high-impact SEO keywords and phrases.
    TOPIC: {topic}
    CONTEXT: {context[:3000]}
    OUTPUT FORMAT: keyword1, keyword2, keyword3...
    """

    # Fallback model list
    candidate_models = ["gemini-1.5-flash-002", "gemini-1.5-pro-002", "gemini-1.5-flash", "gemini-pro"]
    
    for model_name in candidate_models:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text.strip()
        except:
            continue
            
    return f"{topic}, viral content, trending, {topic} news"

def deep_research(topic, api_key, reference_url=None):
    """
    Performs an iterative 'Deep Research' loop.
    1. Scrape Reference URL (if provided)
    2. Initial Search
    3. Analyze & Plan Follow-up
    4. Follow-up Search
    """
    print(f"\n🕵️ Deep Researcher Agent starting for: '{topic}'")
    genai.configure(api_key=api_key)
    
    context_data = []
    sources = []

    # Phase 0: Reference URL (The "Must Have" source if provided)
    if reference_url:
        print(f"  ⬇️ Scraping Reference URL: {reference_url}...")
        ref_content = scrape_content(reference_url)
        if ref_content:
            context_data.append(f"PRIMARY REFERENCE (User Provided): {reference_url}\nCONTENT: {ref_content}\n")
            sources.append({'title': 'User Reference', 'href': reference_url})

    # Phase 1: Initial Broad Search
    print("\n--- Phase 1: Initial Recon ---")
    initial_results = search_web(f"{topic} news facts 2025", max_results=3)
    
    for res in initial_results:
        # Avoid re-scraping the reference url if it appears in search
        if reference_url and res['href'] == reference_url:
            continue
            
        content = scrape_content(res['href'])
        if content:
            context_data.append(f"SOURCE: {res['title']}\nCONTENT: {content}\n")
            sources.append({'title': res.get('title', 'Source'), 'href': res['href']})
            
    initial_context = "\n".join(context_data)
    
    # Phase 2: Reasoning & Gap Analysis
    print("\n--- Phase 2: Reasoning & Gap Analysis ---")
    reasoning_prompt = f"""
    I am researching: "{topic}".
    Here is what I found so far:
    {initial_context[:4000]}
    
    What critical information is missing to write a comprehensive, expert-level article?
    Generate 2 specific, targeted search queries to find this missing info.
    OUTPUT FORMAT: Query 1 | Query 2
    """
    
    follow_up_queries = []
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(reasoning_prompt)
        queries = response.text.strip().split("|")
        follow_up_queries = [q.strip() for q in queries if q.strip()]
        print(f"  🧠 Missing Info Identified. Searching for: {follow_up_queries}")
    except Exception as e:
        print(f"  ⚠️ Reasoning failed, skipping deep dive: {e}")
        
    # Phase 3: Targeted Deep Dive
    if follow_up_queries:
        print("\n--- Phase 3: Targeted Deep Dive ---")
        for query in follow_up_queries:
            deep_results = search_web(query, max_results=1) # Just get the best one
            for res in deep_results:
                # Avoid duplicates
                if not any(s['href'] == res['href'] for s in sources):
                    content = scrape_content(res['href'])
                    if content:
                        context_data.append(f"SOURCE: {res['title']} (Deep Dive)\nCONTENT: {content}\n")
                        sources.append({'title': res.get('title', 'Source'), 'href': res['href']})

    full_context = "\n".join(context_data)
    
    # Generate Keywords
    keywords = generate_keywords(topic, full_context, api_key)
    
    print("✅ Deep Research complete.")
    return full_context, keywords, sources

def process_url(url, api_key):
    """Scrapes a URL and generates keywords (Stealth Mode)."""
    print(f"  ⬇️ Scraping URL (Stealth): {url}...")
    original_content = scrape_content(url)
    
    if not original_content:
        return "Failed to scrape URL.", "generic, content, error", []

    print("  🧠 Analyzing content...")
    # ... (Keep existing topic extraction logic if needed, or simplify) ...
    # For brevity, reusing the simple keyword generation
    keywords = generate_keywords("Analysis", original_content, api_key)
    
    sources = [{'title': 'Primary Source', 'href': url}]
    return f"PRIMARY SOURCE: {url}\nCONTENT: {original_content}", keywords, sources

# Alias for main.py compatibility
research_topic = deep_research
