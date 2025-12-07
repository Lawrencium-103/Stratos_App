import streamlit as st
import base64

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

import io
from docx import Document
from docx.shared import Pt

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
