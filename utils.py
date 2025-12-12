import streamlit as st
import base64
import io
from docx import Document
from docx.shared import Pt

def load_css():
    """
    Injects the 'STRATOS Premium' Dark & Gold CSS theme.
    """
    st.markdown("""
        <style>
        /* Main Background */
        .stApp {
            background-color: #0E1117;
            color: #FAFAFA;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #161B22;
            border-right: 1px solid #30363D;
        }
        
        /* Headers */
        h1, h2, h3 {
            font-family: 'Helvetica Neue', sans-serif;
            font-weight: 700;
            color: #FFD700 !important; /* Gold */
            letter-spacing: -0.5px;
        }
        
        /* Buttons */
        .stButton > button {
            background-color: #1F6FEB;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            background-color: #FFD700;
            color: black;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(255, 215, 0, 0.3);
        }
        
        /* Inputs */
        .stTextInput > div > div > input {
            background-color: #0D1117;
            color: white;
            border: 1px solid #30363D;
            border-radius: 6px;
        }
        .stTextInput > div > div > input:focus {
            border-color: #FFD700;
            box-shadow: 0 0 0 1px #FFD700;
        }
        
        /* Cards / Containers */
        div[data-testid="stExpander"] {
            background-color: #161B22;
            border: 1px solid #30363D;
            border-radius: 8px;
        }
        
        /* Success/Info Messages */
        .stAlert {
            background-color: #161B22;
            border: 1px solid #30363D;
            color: #FAFAFA;
        }
        
        /* Custom Footer */
        footer {visibility: hidden;}
        
        </style>
    """, unsafe_allow_html=True)

def header(title, subtitle=None):
    st.markdown(f"# ⚡ {title}")
    if subtitle:
        st.markdown(f"### *{subtitle}*")
    st.markdown("---")

def create_docx(markdown_text):
    """
    Converts simple Markdown text to a Word Document binary stream.
    Handles Headers (#) and basic text.
    """
    doc = Document()
    
    # Set style
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(11)
    
    lines = markdown_text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('# '):
            doc.add_heading(line.replace('# ', ''), level=1)
        elif line.startswith('## '):
            doc.add_heading(line.replace('## ', ''), level=2)
        elif line.startswith('### '):
            doc.add_heading(line.replace('### ', ''), level=3)
        elif line.startswith('- '):
            doc.add_paragraph(line.replace('- ', ''), style='List Bullet')
        else:
            doc.add_paragraph(line)
            
    # Save to memory buffer
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

def display_impact_metrics():
    """
    Displays the 'Stratos Impact' section with metrics and share buttons.
    """
    st.markdown("---")
    st.subheader("🚀 Stratos Impact")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="Time Saved", value="~12 hrs", delta="95%")
    with col2:
        st.metric(label="Content Velocity", value="10x", delta="High")
    with col3:
        st.metric(label="Strategic Depth", value="Top 1%", delta="Elite")
    with col4:
        st.metric(label="Cost Efficiency", value="$500+", delta="Saved")
        
    st.markdown("### 📢 Share Your Strategy")
    
    # Social Share Links
    share_text = "I just architected my entire content strategy in seconds with Stratos AI! ⚡ #StratosAI #ContentStrategy"
    share_url = "https://stratos-app.streamlit.app" # Replace with actual URL if known
    
    twitter_url = f"https://twitter.com/intent/tweet?text={share_text}&url={share_url}"
    linkedin_url = f"https://www.linkedin.com/sharing/share-offsite/?url={share_url}"
    
    c1, c2 = st.columns(2)
    with c1:
        st.link_button("🐦 Share on X (Twitter)", twitter_url)
    with c2:
        st.link_button("💼 Share on LinkedIn", linkedin_url)
