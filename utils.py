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

def track_usage(platform_type):
    """
    Tracks usage stats in Session State.
    platform_type: 'LinkedIn' (3 hrs saved) or 'Twitter' (1 hr saved) or 'Blog' (4 hrs)
    """
    if 'hours_saved' not in st.session_state: st.session_state['hours_saved'] = 0.0
    if 'content_count' not in st.session_state: st.session_state['content_count'] = 0
    
    saved = 0
    if platform_type == 'LinkedIn': saved = 3.0
    elif platform_type == 'Twitter': saved = 1.0
    elif platform_type == 'Blog': saved = 4.0
    else: saved = 0.5
    
    st.session_state['hours_saved'] += saved
    st.session_state['content_count'] += 1

def display_impact_metrics():
    """
    Displays the 'Stratos Impact' section with dynamic metrics, like button, and smart sharing.
    """
    st.markdown("---")
    st.subheader("🚀 Stratos Impact")
    
    # Initialize Session State metrics if not present
    if 'hours_saved' not in st.session_state: st.session_state['hours_saved'] = 0.0
    if 'content_count' not in st.session_state: st.session_state['content_count'] = 0
    if 'likes' not in st.session_state: st.session_state['likes'] = 0
    
    # Metrics Columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="Hours Saved (You)", value=f"{st.session_state['hours_saved']} hrs", delta="Efficiency")
    with col2:
        # Simulated "Global" Average (Static for now, but illustrative)
        avg_saved = 1250 + int(st.session_state['hours_saved'] * 10)
        st.metric(label="Community Hours Saved", value=f"{avg_saved}+ hrs", delta="Global")
    with col3:
        st.metric(label="Content Pieces Generated", value=st.session_state['content_count'])
    with col4:
        # Like Button Logic
        if st.button("❤️ Like Stratos"):
            if st.session_state['likes'] < 3:
                st.session_state['likes'] += 1
                st.toast("Thanks for the love! ❤️")
            else:
                st.toast("You've reached the max likes for this session! Spread the word instead! 🚀")
        st.write(f"Session Likes: {st.session_state['likes']}/3")
        
    st.markdown("### 📢 Share Your Strategy")
    st.info("💡 **Pro Tip:** The best way to share is to copy your generated content directly!")
    
    # Social Share Links (Pre-filled text)
    share_text = f"I just saved {st.session_state['hours_saved']} hours on my content strategy using Stratos AI! ⚡ #StratosAI #ContentStrategy"
    share_url = "https://stratos-app.streamlit.app"
    
    twitter_url = f"https://twitter.com/intent/tweet?text={share_text}&url={share_url}"
    linkedin_url = f"https://www.linkedin.com/sharing/share-offsite/?url={share_url}"
    
    c1, c2 = st.columns(2)
    with c1:
        st.link_button("🐦 Tweet Your Savings", twitter_url)
    with c2:
        st.link_button("💼 Share on LinkedIn", linkedin_url)
