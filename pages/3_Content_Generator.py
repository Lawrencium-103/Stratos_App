import streamlit as st
import os
from dotenv import load_dotenv
import llm_client
import researcher
import utils

# Load environment variables
load_dotenv()

# Get API key
api_key = llm_client.get_api_key()

st.set_page_config(page_title="STRATOS: Generator", page_icon="✍️", layout="wide")

# Apply Branding
utils.load_css()
utils.header("STRATOS: Content Generator", "Create Viral, AEO-Optimized Content")

# Load System Prompt
def load_prompt():
    try:
        with open(os.path.join("prompts", "master_system_prompt.txt"), "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "You are an expert copywriter."

system_instruction = load_prompt()

# Initialize Session State
if 'gen_topic' not in st.session_state: st.session_state['gen_topic'] = ""
if 'gen_scraped_data' not in st.session_state: st.session_state['gen_scraped_data'] = ""
if 'gen_keywords' not in st.session_state: st.session_state['gen_keywords'] = ""
if 'gen_sources' not in st.session_state: st.session_state['gen_sources'] = []

# Sidebar Reset
with st.sidebar:
    if st.button("🔄 Reset Generator"):
        for key in ['gen_topic', 'gen_scraped_data', 'gen_keywords', 'gen_sources']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# Unified Input Section
st.markdown("### 1. Define Your Strategy")
st.markdown("Enter a Topic (Required) and optionally a URL to guide the research.")

col1, col2 = st.columns(2)
with col1:
    topic_input = st.text_input("Enter Topic / Keyword *", placeholder="e.g. Future of AI in Healthcare")
with col2:
    url_input = st.text_input("Reference URL (Optional)", placeholder="https://example.com/article")

if st.button("🚀 Start Research"):
    if topic_input and api_key:
        with st.spinner("🕵️ Deep Researching Topic & Analyzing Sources..."):
            # Call the updated deep_research with both arguments
            data, kw, src = researcher.research_topic(topic_input, api_key, reference_url=url_input)
            
            st.session_state['gen_topic'] = topic_input
            st.session_state['gen_scraped_data'] = data
            st.session_state['gen_keywords'] = kw
            st.session_state['gen_sources'] = src
            st.success("Research Complete!")
            
    elif not topic_input:
        st.warning("⚠️ Please enter a Topic.")
    elif not api_key:
        st.error("Missing API Key")

# Content Generation Section
if st.session_state['gen_scraped_data']:
    st.divider()
    st.subheader("Research Context")
    with st.expander("View Gathered Data"):
        st.text(st.session_state['gen_scraped_data'][:2000] + "...")
    
    st.info(f"**Keywords:** {st.session_state['gen_keywords']}")
    
    # --- Personal Attribution Section ---
    st.markdown("### 2. Personal Attribution (Optional)")
    use_attribution = st.checkbox("Include Personal Attribution / Industry Reference")
    
    attribution_instruction = ""
    if use_attribution:
        attr_text = st.text_area("Attribution Content (Quote, Insight, or Author Reference)", 
                                 placeholder="e.g. 'As Dr. Smith says, prevention is better than cure.'")
        attr_platforms = st.multiselect("Apply to Platforms", 
                                        ["LinkedIn", "X (Twitter)", "Instagram/Facebook", "Reddit", "Threads", "Blog Post 1"], 
                                        default=["LinkedIn"])
        
        if attr_text and attr_platforms:
            attribution_instruction = f"""
            *** PERSONAL ATTRIBUTION INSTRUCTION ***
            For the following platforms ONLY: {', '.join(attr_platforms)}
            You MUST naturally weave in the following reference/attribution:
            "{attr_text}"
            
            Constraint: Do NOT just paste it. Integrate it as a "Industry Thought" or "Expert Validation" that adds weight to the argument. It must feel like a genuine connection, not a forced shout-out.
            """

    # --- 3. Target Platforms ---
    st.markdown("### 3. Target Platforms")
    all_platforms = ["LinkedIn", "X (Twitter)", "Instagram/Facebook", "Reddit", "Threads", "Blog Post 1", "AEO Answer Card"]
    default_platforms = ["AEO Answer Card", "LinkedIn", "Blog Post 1", "X (Twitter)"]
    target_platforms = st.multiselect("Select Content to Generate", all_platforms, default=default_platforms)

    # --- 4. AI Controls ---
    st.markdown("### 4. AI Controls")
    temperature = st.slider("Creativity / Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1, help="Lower = More Factual/Strict. Higher = More Creative/Viral.")

    if st.button("✨ Ignite Viral Engine"):
        if not target_platforms:
            st.error("⚠️ Please select at least one platform.")
        else:
            # Track Usage
            for p in target_platforms:
                if "LinkedIn" in p: utils.track_usage('LinkedIn')
                elif "Twitter" in p or "X" in p: utils.track_usage('Twitter')
                elif "Blog" in p: utils.track_usage('Blog')
                else: utils.track_usage('Other')

            # Prepare Model
            # llm_client handles configuration
            
            user_message = f"""
            TOPIC: {st.session_state['gen_topic']}
            SCRAPED CONTEXT (Facts/News): {st.session_state['gen_scraped_data']}
            SEO KEYWORDS: {st.session_state['gen_keywords']}

            {attribution_instruction}

            *** GENERATION INSTRUCTION ***
            You must generate content ONLY for the following selected platforms:
            {', '.join(target_platforms)}
            
            **CRITICAL FORMATTING RULE:**
            - Do NOT wrap the entire output in a markdown code block (i.e., do NOT use ```markdown).
            - Output CLEAN, renderable markdown.
            - Use bolding, italics, and headers to make it look "ready to publish".
            
            Do NOT generate content for any other platforms.
            
            --- PLATFORM SPECIFIC RULES (STRICT) ---
            
            1. LINKEDIN (The "Strategic Thought Leader"):
               - **Goal:** Drive business conversations and authority.
               - **Length:** **200 - 450 Words.** (Substantial but concise).
               - **Structure:**
                 - **The Hook:** Start with a contrarian statement or a hard truth about the industry.
                 - **The Context:** Briefly explain why this matters NOW (Business impact/ROI).
                 - **The Insight:** Provide 3-4 actionable, high-level strategic points. **EXPAND on each point.** Do not just list them. Write 2-3 sentences per point explaining the "Why" and "How". Make it educational and grounded.
                 - **The Close:** End with a question that demands a comment.
               - **Tone:** Professional, authoritative, yet conversational. NO "In today's fast-paced world."
            
            2. X (TWITTER) THREAD (The "Viral Opinion"):
               - **Goal:** Maximum engagement and retweets.
               - **Structure:**
                 - **Tweet 1 (The Hook):** A short, punchy, provocative statement. No hashtags here. Just raw opinion.
                 - **Tweet 2:** The "Meat". Why is the hook true?
                 - **Tweets 3-6:** Specific examples, data points, or "mental models" to explain the concept. One idea per tweet.
                 - **Tweet 7 (The Summary):** A TL;DR bullet list of the thread.
                 - **Tweet 8 (The CTA):** "If you found this useful, follow me for more on [Niche]."
               - **Tone:** Fast, punchy, slightly aggressive or "edgy". Use line breaks for rhythm.
            
            3. INSTAGRAM / FACEBOOK (The "Visual Storyteller"):
               - **Goal:** Stop the scroll with visuals + story.
               - **Structure:**
                 - **Slide 1 (Image Prompt):** Describe a high-contrast, stopping image.
                 - **Slide 1 (Text Overlay):** A 5-word hook.
                 - **Caption:** Write a "Micro-Blog" (150-200 words). Tell a story or give a specific tip. Use short paragraphs.
                 - **Hashtags:** List 10 relevant hashtags.
            
            4. THREADS (The "Casual Conversation"):
               - **Goal:** Spark a discussion.
               - **Length:** **Short & Punchy (< 500 Characters).**
               - **Structure:**
                 - **Post:** A single, thought-provoking question or observation.
                 - **Tone:** Casual, like texting a friend. "Hot take: [Opinion]." No hashtags needed.
            
            5. REDDIT (The "Community Insider"):
               - **Goal:** Provide genuine value to a specific subreddit.
               - **Length:** **200 - 450 Words.**
               - **Structure:**
                 - **Title:** A specific question or "How I..." statement. (e.g., "How I solved X").
                 - **Body:** Share a personal story, a specific tactic, or a "Lessons Learned" list.
                 - **Tone:** "Internet Native", authentic, humble. NO marketing fluff. NO "In this post". Just talk like a human.
            
            5. BLOG POST (The "Deep Dive Authority"):
               - **Goal:** Rank on Google and serve as a "Comprehensive Guide".
               - **Length:** **MINIMUM 1,000 WORDS.** (Target: 1,500+).
               - **Structure:**
                 - **Title:** SEO-Optimized, Clickable Title (e.g., "The Ultimate Guide to...").
                 - **Introduction:** Hook the reader, define the problem, and state the thesis.
                 - **Body:** Use H2 and H3 headers. You MUST write **at least 300 words per section** below:
                   - "What is [Topic]?" (Definition & Context)
                   - "Why it Matters" (Data/Stats - Use the Research)
                   - "Key Strategies/Examples" (The Core Value - Go Deep)
                   - "Common Pitfalls"
                 - **Conclusion:** Summary and final thought.
               - **Content Depth:** **IGNORE BREVITY.** Write a GUIDE. Use specific examples, analogies, and technical details. If you find yourself summarizing, STOP and EXPAND.
            
            6. AEO ANSWER CARD (If selected):
               - **Length:** **500 - 1,000 Words.** (Comprehensive Answer).
               - Start with a Direct Definition (No Intro).
               - Use Question Headers.
               - End with an FAQ Section.
            
            --- CRITICAL ATTRIBUTION CHECK ---
            If an attribution was provided above, you **MUST** include it in the output for the selected platforms. Failure to include the quote/reference is a failure of the task.
            
            --- QUALITY & LENGTH CHECK ---
            - **Blog:** Is it at least 1000 words? Did you cover all sections in depth?
            - **AEO:** Is it comprehensive (500+ words)?
            - **LinkedIn/Reddit:** Is it between 200-450 words?
            - **General:** Does it maintain high standards? (No fluff, just value).
            """
        
        st.markdown("### 👁️ Live Content Preview")
        st.caption("This is how your content will look to your audience.")
        
        # Styled Container for Preview
        with st.container(border=True):
            output_container = st.empty()
        
        full_text = ""
        
        # Candidate models for fallback
        candidate_models = [
            "meta-llama/llama-3.1-70b-instruct",
            "meta-llama/llama-3.1-8b-instruct"
        ]
        
        success = False
        last_error = None

        for model_name in candidate_models:
            try:
                # llm_client.generate returns a generator if stream=True
                response_stream = llm_client.generate(
                    prompt=user_message,
                    system_instruction=system_instruction,
                    model=model_name,
                    stream=True,
                    api_key=api_key,
                    temperature=temperature
                )
                
                for chunk in response_stream:
                    full_text += chunk.text
                    output_container.markdown(full_text + "▌")
                
                # Final render without cursor
                output_container.markdown(full_text)
                
                # Copy to Clipboard Feature
                st.markdown("---")
                st.markdown("### 📋 Raw Text (For Copying)")
                st.code(full_text, language="markdown")
                st.caption("Click the copy icon in the top right of the code block above to copy everything!")
                success = True
                break # Stop if successful
                
            except Exception as e:
                last_error = e
                continue # Try next model
        
        if not success:
            st.error(f"Generation Failed: All models failed. Last error: {last_error}")
            
        if success:
            # References
            st.markdown("### 📚 References")
            for s in st.session_state['gen_sources']:
                st.markdown(f"- [{s.get('title', 'Source')}]({s['href']})")
                
            # Download
            # Download
            docx_file = utils.create_docx(full_text)
            st.download_button(
                label="📄 Download Content (Word Doc)",
                data=docx_file,
                file_name="generated_content.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

# Show Impact Metrics
utils.display_impact_metrics()
