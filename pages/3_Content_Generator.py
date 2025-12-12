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
