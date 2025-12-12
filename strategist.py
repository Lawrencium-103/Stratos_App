import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
import llm_client
import os
from fake_useragent import UserAgent

def get_stealth_headers():
    try:
        ua = UserAgent()
        return {'User-Agent': ua.random, 'Referer': 'https://www.google.com/'}
    except:
        return {'User-Agent': 'Mozilla/5.0'}

def crawl_site(url):
    """
    Scrapes the homepage and extracts main headings/meta description 
    to understand what the site is about.
    """
    try:
        response = requests.get(url, headers=get_stealth_headers(), timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.title.string if soup.title else "No Title"
        meta_desc = ""
        meta_tag = soup.find('meta', attrs={'name': 'description'})
        if meta_tag:
            meta_desc = meta_tag.get('content')
            
        h1s = [h.get_text(strip=True) for h in soup.find_all('h1')]
        h2s = [h.get_text(strip=True) for h in soup.find_all('h2')[:5]] # Top 5 H2s
        
        # Try to find nav links to understand structure
        nav_links = []
        nav = soup.find('nav')
        if nav:
            for link in nav.find_all('a')[:10]:
                nav_links.append(link.get_text(strip=True))
                
        return f"""
        URL: {url}
        Title: {title}
        Description: {meta_desc}
        Main Headings: {h1s}
        Sub Headings: {h2s}
        Navigation/Categories: {nav_links}
        """
    except Exception as e:
        return f"Error crawling {url}: {e}"

def find_competitors(niche):
    """
    Uses DuckDuckGo to find top ranking sites for the niche.
    """
    print(f"  🕵️  Scouting for top competitors in '{niche}'...")
    competitors = []
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(f"best {niche} blogs websites", max_results=5))
            for r in results:
                # Filter out generic sites like reddit, quora, medium if possible, but for now just take top 3
                if "reddit" not in r['href'] and "quora" not in r['href']:
                    competitors.append(r['href'])
                    if len(competitors) >= 3:
                        break
    except Exception as e:
        print(f"  ⚠️  Could not auto-discover competitors: {e}")
    
    return competitors

def generate_roadmap(niche, user_url, manual_competitors, api_key):
    """
    Orchestrates the strategy generation.
    """
    """
    Orchestrates the strategy generation.
    """
    # genai.configure(api_key=api_key) - Handled by llm_client
    
    # 1. Analyze User Site (if provided)
    user_context = "User has no existing site."
    if user_url:
        print(f"  🏠 Analyzing your site: {user_url}...")
        user_context = crawl_site(user_url)
        
    # 2. Analyze Competitors
    competitor_urls = manual_competitors if manual_competitors else []
    
    # Auto-discover if we don't have enough manual ones (aim for 3 total)
    if len(competitor_urls) < 3:
        auto_competitors = find_competitors(niche)
        # Add unique ones
        for url in auto_competitors:
            if url not in competitor_urls:
                competitor_urls.append(url)
                
    competitor_context = ""
    print(f"  ⚔️  Analyzing competitors: {competitor_urls}...")
    for url in competitor_urls[:3]: # Limit to 3 to save time/tokens
        print(f"     ⬇️ Crawling {url}...")
        data = crawl_site(url)
        competitor_context += f"\n--- COMPETITOR: {url} ---\n{data}\n"

    # 3. Analyze User Intent (Autocomplete) - NEW
    print(f"  🔮 Analyzing User Intent for '{niche}'...")
    import researcher # Import here to avoid circular dependency at top level if any
    suggestions = researcher.get_google_suggestions(niche)
    suggestions_str = ", ".join(suggestions) if suggestions else "No specific autocomplete data found."
        
    # 4. Generate Strategy
    print("\n  🧠 The Strategist is building your roadmap...")
    
    # Load Prompt
    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "strategy_system_prompt.txt")
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            system_instruction = f.read()
    except:
        system_instruction = "You are a Content Strategist."

    user_message = f"""
    NICHE: {niche}
    
    USER_CONTEXT:
    {user_context}
    
    COMPETITOR_CONTEXT:
    {competitor_context}
    
    USER INTENT (REAL-TIME SEARCHES):
    {suggestions_str}
    
    *** CRITICAL INSTRUCTION FOR ROADMAP ***
    You must identify "Content Gaps" - topics that users are searching for (User Intent) but are NOT fully covered by competitors.
    
    When listing topics under Pillars, use this format:
    - For standard topics: "#### 1. Topic Name"
    - For HIGH DEMAND / UNTAPPED OPPORTUNITIES (based on User Intent): "#### [OPPORTUNITY] Topic Name"
    
    Ensure at least 30% of the topics are marked as [OPPORTUNITY] if the data supports it.
    """

    # Use OpenRouter via llm_client
    # Primary: Llama 3.1 70B (Smart)
    # Fallback: Llama 3.1 8B (Fast)
    candidate_models = [
        "meta-llama/llama-3.1-70b-instruct",
        "meta-llama/llama-3.1-8b-instruct"
    ]

    response = None
    for model_name in candidate_models:
        try:
            print(f"   Trying model: {model_name}...")
            # llm_client.generate returns a generator if stream=True
            response = llm_client.generate(
                prompt=user_message,
                system_instruction=system_instruction,
                model=model_name,
                stream=True
            )
            break # Success
        except Exception as e:
            print(f"   ❌ Failed with {model_name}: {e}")
            continue
            
    if not response:
        return "Error: All models failed to generate the roadmap."
    
    print("\n" + "="*30)
    print("   STRATEGIC CONTENT ROADMAP   ")
    print("="*30 + "\n")
    
    full_text = ""
    for chunk in response:
        print(chunk.text, end="", flush=True)
        full_text += chunk.text
        
    return full_text
