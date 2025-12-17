import streamlit as st
import researcher
import llm_client
import utils
import time

# --- Configuration ---
st.set_page_config(page_title="STRATOS: The Alchemist", page_icon="⚗️", layout="wide")
utils.load_css()
utils.header("The Alchemist", "Turn Competitor Lead into Authority Gold")

# --- Introduction ---
st.markdown("""
<div style='background-color: #161B22; padding: 15px; border-radius: 10px; border: 1px solid #30363D; margin-bottom: 20px;'>
    <h4 style='color: #FFD700; margin: 0;'>⚗️ The Transmutation Process</h4>
    <p style='color: #b0b8c6; margin-top: 10px;'>
        <b>Alchemy</b> is the art of transformation. This engine takes the raw materials of the web (competitor articles), 
        extracts their essence (DNA), and fuses it with your unique insight to create <b>Golden Content</b> that is impossible to ignore.
    </p>
</div>
""", unsafe_allow_html=True)

# --- Session State ---
if 'rep_content' not in st.session_state: st.session_state['rep_content'] = ""

# --- Inputs ---
st.markdown("### 1. Source Material (The Competition)")
target_keyword = st.text_input("Target Keyword *", placeholder="e.g. Best Solar Panels in Nigeria")

# Input Method Toggle
input_method = st.radio("Input Method:", ["URLs (Auto-Scrape)", "Raw Text (Manual Paste)"], horizontal=True)

competitors = []
if input_method == "URLs (Auto-Scrape)":
    c1, c2, c3 = st.columns(3)
    with c1: url1 = st.text_input("Competitor URL #1")
    with c2: url2 = st.text_input("Competitor URL #2")
    with c3: url3 = st.text_input("Competitor URL #3")
    
    if url1: competitors.append({"type": "url", "data": url1})
    if url2: competitors.append({"type": "url", "data": url2})
    if url3: competitors.append({"type": "url", "data": url3})

else:
    st.info("💡 Use this if the URL scraper is being blocked.")
    t1 = st.text_area("Competitor Text #1", height=150)
    t2 = st.text_area("Competitor Text #2", height=150)
    t3 = st.text_area("Competitor Text #3", height=150)
    
    if t1: competitors.append({"type": "text", "data": t1})
    if t2: competitors.append({"type": "text", "data": t2})
    if t3: competitors.append({"type": "text", "data": t3})

st.markdown("### 2. Your Knowledge Extraction")
st.info("💡 The AI will copy the *Structure* of competitors, but it needs *Your Facts* to make it original.")

user_data = st.text_area("Your Specific Insights / Data / Products (Critical)", 
                        placeholder="Paste your rough notes, product specs, or specific arguments you want included here. \nExample: 'Our panels differ because they use Mono-PERC technology. We offer a 25-year warranty, not 10.'\n(If you leave this blank, the AI will rely 100% on competitors, which is risky.)")

user_angle = st.text_input("Brand Tone / Angle", placeholder="e.g. Professional, Contrarian, Friendly")

# --- Generation Logic ---
if st.button("🧬 Replicate & Upgrade content"):
    if not target_keyword:
        st.error("⚠️ Please enter a Target Keyword.")
    elif not competitors:
        st.error("⚠️ Please provide at least one Competitor Source.")
    else:
        api_key = llm_client.get_api_key()
        if not api_key:
            st.error("Missing API Key.")
        else:
            status_container = st.empty()
            
            # 1. Scrape / Gather Data
            analyzed_content = ""
            
            with st.spinner("🕵️ Extracting Competitor DNA..."):
                for i, comp in enumerate(competitors):
                    status_container.markdown(f"**Analyzing Source {i+1}...**")
                    
                    if comp['type'] == 'url':
                        # Use the NEW structured scraper
                        content = researcher.scrape_content_with_markdown(comp['data'])
                        if content:
                            analyzed_content += f"\n--- COMPETITOR {i+1} ({comp['data']}) ---\n{content}\n"
                        else:
                            st.warning(f"Failed to scrape Source {i+1}. Skipping.")
                    else:
                        analyzed_content += f"\n--- COMPETITOR {i+1} (Manual Text) ---\n{comp['data']}\n"
            
            if not analyzed_content:
                st.error("Could not extract any content from sources.")
            else:
                # 2. The REPLICATOR Prompt
                system_prompt = "You are an Elite SEO Editor and Content Strategist. Your job is to execute the 'Skyscraper Technique'."
                
                user_prompt = f"""
                TARGET KEYWORD: {target_keyword}
                MY SPECIFIC KNOWLEDGE: {user_data}
                MY BRAND TONE: {user_angle}
                
                Here is the Raw Content from the Top Ranking Competitors:
                {analyzed_content[:25000]} 
                
                *** MISSION ***
                1. ANALYZE the competitors for STRUCTURE and RANKING FACTORS.
                2. USE their structure, BUT...
                3. FILL it with *MY SPECIFIC KNOWLEDGE* (provided above). 
                *** CRITICAL: COHESION & FLOW ***
                - The final article must read as **ONE unified voice**. 
                - Do NOT simply append sections from different competitors like a "Frankenstein" monster. 
                - You must **weave** them together with smooth transitions. 
                - The reader should NOT be able to tell this came from multiple sources.
                
                *** OUTPUT REQUIREMENTS ***
                
                PART 1: THE AUTHORITY BLOG POST (The "Skyscraper")
                - Length: **2,000+ Words**.
                - Structure: Use the combined H2/H3 structure from the competitors, but organize it more logically.
                - Depth: If Competitor A has a definition and Competitor B has an example, you must include ALL OF IT.
                - Tone: Professional, authoritative, yet engaging.
                
                PART 2: THE AEO "DATA ENGINE" (For AI Search)
                - This section is designed specifically for AI Bots (Perplexity, Google SGE) to read.
                - **Length:** 500-800 Words of Pure Structured Data.
                - Format:
                  - **Direct Answer Block:** A 50-word perfect definition of the query.
                  - **Comparison Tables:** Compare products/methods using Markdown Tables.
                  - **Bullet Lists:** "Top 10 Factors", "Key Statistics".
                  - **FAQ Schema:** 5 Questions users ask, with direct answers.
                
                *** FORMATTING ***
                - Use clear Markdown (# H1, ## H2).
                - Do NOT use code blocks.
                - Make it "Ready to Publish".
                """
                
                # 3. Generate
                with st.spinner("🧬 Synthesizing Super-Article... (This requires deep thought)"):
                    try:
                        # Using 70b (High Intelligence) is mandatory here
                        stream = llm_client.generate(user_prompt, system_prompt, model="meta-llama/llama-3.1-70b-instruct", stream=True, api_key=api_key)
                        
                        full_text = ""
                        output_container = st.empty()
                        
                        for chunk in stream:
                            if hasattr(chunk, 'choices') and chunk.choices: # OpenRouter standard chunk
                                content = chunk.choices[0].delta.content
                                if content:
                                    full_text += content
                                    output_container.markdown(full_text + "▌")
                            elif hasattr(chunk, 'text'): # Custom wrapper
                                full_text += chunk.text
                                output_container.markdown(full_text + "▌")
                                
                        output_container.markdown(full_text)
                        st.session_state['rep_content'] = full_text
                        
                    except Exception as e:
                        st.error(f"Generation Failed: {e}")

# --- Output Actions ---
if st.session_state['rep_content']:
    st.markdown("---")
    st.success("🧬 Replication Complete.")
    
    # Download
    docx = utils.create_docx(st.session_state['rep_content'])
    st.download_button(
        "📄 Download Skyscraper Content (Word)",
        data=docx,
        file_name=f"Skyscraper_{target_keyword.replace(' ', '_')}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

    # Copy
    st.markdown("### 📋 Copy Code")
    st.code(st.session_state['rep_content'], language="markdown")

# Impact Metrics
utils.display_impact_metrics()
