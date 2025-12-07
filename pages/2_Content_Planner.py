import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
import utils
import researcher

# Load Environment
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Apply Branding
utils.load_css()
utils.header("STRATOS: Content Planner", "Architect Your Content Empire")

# Initialize Session State for Plan
if 'plan_generated' not in st.session_state: st.session_state['plan_generated'] = False
if 'plan_content' not in st.session_state: st.session_state['plan_content'] = ""

# --- 1. Configuration ---
st.markdown("### 1. Plan Configuration")
col1, col2 = st.columns(2)

with col1:
    duration = st.radio("Select Duration", ["1 Week Sprint", "1 Month Strategy", "3 Month Roadmap"])

with col2:
    st.markdown("**Data Sources:**")
    use_app_data = st.checkbox("Use 'Strategist' Data (Niche/Pillars)", value=True)
    use_custom_data = st.checkbox("Use Custom Input / Notes", value=False)

# --- 2. Custom Input (Conditional) ---
custom_notes = ""
if use_custom_data:
    custom_notes = st.text_area("Enter Custom Goals, Topics, or Notes:", placeholder="e.g. Focus on launching our new AI feature next week...")
    supplement_crawling = st.checkbox("🕵️ Supplement Custom Input with Web Research (Recommended for SEO)")

# --- 3. Generation Logic ---
if st.button("📅 Architect My Content Empire"):
    if not api_key:
        st.error("Missing API Key")
    else:
        # Gather Context
        context_parts = []
        
        # Part A: App Data
        if use_app_data:
            if 'roadmap_text' in st.session_state and st.session_state['roadmap_text']:
                context_parts.append(f"STRATEGIC ROADMAP:\n{st.session_state['roadmap_text']}")
            else:
                st.warning("⚠️ No Strategist Data found. Please run the 'Strategist' first or uncheck 'Use Strategist Data'.")
        
        # Part B: Custom Data + Research
        if use_custom_data and custom_notes:
            context_parts.append(f"USER NOTES:\n{custom_notes}")
            
            if supplement_crawling:
                with st.spinner("🕵️ Researching your custom notes for SEO trends..."):
                    # Quick research on the notes
                    data, kw, src = researcher.research_topic(custom_notes, api_key)
                    context_parts.append(f"WEB RESEARCH ON NOTES:\n{data}\nKEYWORDS: {kw}")
        
        if not context_parts:
            st.error("Please select at least one data source and ensure data is available.")
        else:
            # Generate
            with st.spinner("🤖 Architecting your Content Schedule..."):
                genai.configure(api_key=api_key)
                
                # Candidate models for fallback
                candidate_models = [
                    "gemini-1.5-flash",
                    "gemini-1.5-flash-8b",
                    "gemini-1.5-pro"
                ]
                
                full_context = "\n\n".join(context_parts)
                
                prompt = f"""
                ROLE: You are an Elite Content Director.
                TASK: Create a {duration} Content Schedule based on the provided context.
                
                CONTEXT:
                {full_context}
                
                OUTPUT FORMAT:
                Generate a Markdown Table with the following columns:
                | Day/Week | Platform | Content Type | Topic / Hook | Tone | Status |
                
                REQUIREMENTS:
                1. Varied Mix: Balance between Educational, Viral, and Sales content.
                2. Platform Native: Specify if it's a Thread (X), Carousel (IG), or Article (LinkedIn).
                3. Strategic Flow: Ensure the topics build upon each other.
                4. If "Web Research" data is present, integrate those trends.
                
                After the table, provide a brief "Execution Strategy" summary (3 bullet points).
                """
                
                success = False
                last_error = None

                for model_name in candidate_models:
                    try:
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content(prompt)
                        st.session_state['plan_content'] = response.text
                        st.session_state['plan_generated'] = True
                        success = True
                        break # Stop if successful
                    except Exception as e:
                        last_error = e
                        continue # Try next model
                
                if success:
                    st.success("Schedule Generated!")
                    st.rerun()
                else:
                    st.error(f"Generation Failed: All models failed. Last error: {last_error}")

# --- 4. Display Results ---
if st.session_state['plan_generated']:
    st.markdown("---")
    st.markdown("### 🗓️ Your Strategic Schedule")
    st.markdown(st.session_state['plan_content'])
    
    # Parse Table for CSV
    import pandas as pd
    import io
    
    try:
        # Extract table part
        content = st.session_state['plan_content']
        if "|" in content:
            # Find start and end of table
            lines = content.split('\n')
            table_lines = [line for line in lines if "|" in line]
            
            if len(table_lines) > 2:
                # Join and read with pandas
                table_str = "\n".join(table_lines)
                # Use StringIO to simulate a file
                df = pd.read_csv(io.StringIO(table_str), sep="|", skipinitialspace=True)
                
                # Clean up pandas parsing artifacts (empty columns from leading/trailing pipes)
                df = df.dropna(axis=1, how='all')
                # Strip whitespace from headers and values
                df.columns = df.columns.str.strip()
                df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
                
                # Convert to CSV
                csv = df.to_csv(index=False).encode('utf-8')
                
                st.download_button(
                    "📥 Download Schedule (CSV)",
                    csv,
                    "stratos_content_plan.csv",
                    "text/csv",
                    key='download-csv'
                )
    except Exception as e:
        st.warning(f"Could not parse table for CSV: {e}")
    
    # Word Doc Option
    docx_file = utils.create_docx(st.session_state['plan_content'])
    st.download_button(
        "📄 Download Schedule (Word)",
        docx_file,
        "stratos_content_plan.docx",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        key='download-docx'
    )
