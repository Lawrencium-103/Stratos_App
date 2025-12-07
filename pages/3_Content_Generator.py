import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import researcher
import utils

# Load environment variables
load_dotenv()

# Get API key from Streamlit secrets (Cloud) or .env (Local)
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    api_key = os.getenv("GOOGLE_API_KEY")

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

    # --- Platform Selection Section ---
    st.markdown("### 3. Target Platforms")
    all_platforms = ["LinkedIn", "X (Twitter)", "Instagram/Facebook", "Reddit", "Threads", "Blog Post 1", "AEO Answer Card"]
    target_platforms = st.multiselect("Select Content to Generate", all_platforms, default=all_platforms)

    if st.button("✨ Ignite Viral Engine"):
        if not target_platforms:
            st.error("⚠️ Please select at least one platform.")
        else:
            # Prepare Model
            genai.configure(api_key=api_key)
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 65536,
            }
            
            user_message = f"""
            TOPIC: {st.session_state['gen_topic']}
            SCRAPED CONTEXT (Facts/News): {st.session_state['gen_scraped_data']}
            SEO KEYWORDS: {st.session_state['gen_keywords']}

            {attribution_instruction}

            *** GENERATION INSTRUCTION ***
            You must generate content ONLY for the following selected platforms:
            {', '.join(target_platforms)}
            
            Do NOT generate content for any other platforms.
            
            IMPORTANT INSTRUCTION FOR "AEO Answer Card" (If selected):
            You MUST follow the strict format:
            1. Start with a Direct Definition (No Intro).
            2. Use Question Headers.
            3. End with an FAQ Section.
            If you fail this structure, the content is useless.
            """
        
        st.markdown("### 📝 Generated Content")
        output_container = st.empty()
        full_text = ""
        
        # Candidate models for fallback
        candidate_models = [
            "gemini-1.5-flash-002",
            "gemini-1.5-pro-002",
            "gemini-1.5-flash",
            "gemini-pro"
        ]
        
        success = False
        last_error = None

        for model_name in candidate_models:
            try:
                # st.write(f"Trying model: {model_name}...") # Debug line (optional)
                model = genai.GenerativeModel(
                    model_name=model_name,
                    generation_config=generation_config,
                    system_instruction=system_instruction
                )
                
                response_stream = model.generate_content(user_message, stream=True)
                
                for chunk in response_stream:
                    full_text += chunk.text
                    output_container.markdown(full_text + "▌")
                
                # Final render without cursor
                output_container.markdown(full_text)
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
