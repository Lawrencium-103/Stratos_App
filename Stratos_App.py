import streamlit as st
import os
import time
from dotenv import load_dotenv
import llm_client
from streamlit_agraph import agraph, Node, Edge, Config
import strategist
import utils

# Load environment variables
load_dotenv()

# Get API key
api_key = llm_client.get_api_key()

st.set_page_config(page_title="STRATOS AI", page_icon="⚡", layout="wide")

# Apply Branding
utils.load_css()
utils.header("STRATOS: The Strategist", "Visual Intelligence & Roadmap Engine")

# Sidebar Inputs
with st.sidebar:
    st.header("Strategy Inputs")
    niche = st.text_input("Niche / Industry", placeholder="e.g. Solar Energy")
    user_url = st.text_input("Your Website URL", placeholder="https://yoursite.com")
    comp_url_1 = st.text_input("Competitor 1 URL", placeholder="Optional")
    comp_url_2 = st.text_input("Competitor 2 URL", placeholder="Optional")
    
    manual_competitors = []
    if comp_url_1: manual_competitors.append(comp_url_1)
    if comp_url_2: manual_competitors.append(comp_url_2)
    
    run_btn = st.button("🚀 Initialize Strategy Engine")

if run_btn and niche and api_key:
    with st.spinner("🕵️ The Strategist is analyzing the web... (This may take 1-2 mins)"):
        # 1. Run the existing text-based strategist
        roadmap_text = strategist.generate_roadmap(niche, user_url, manual_competitors, api_key)
        
        st.session_state['roadmap_text'] = roadmap_text
        st.session_state['graph_generated'] = True
        st.rerun()

# Display Results if generated
if st.session_state.get('graph_generated'):
    st.success("Analysis Complete!")
    
    roadmap_text = st.session_state['roadmap_text']
    
    # 2. Visualize the Graph
    st.subheader("Interactive Content Graph")
    
    nodes = []
    edges = []
    
    # Helper to truncate labels
    def truncate(text, limit=25):
        return text[:limit] + "..." if len(text) > limit else text

    # Central Node (The Niche)
    nodes.append(Node(id="ROOT", label=niche, size=50, color="#FFD700", font={'size': 24, 'color': 'black', 'face': 'arial'})) # Gold, Big Hub

    # Parse the roadmap text
    lines = roadmap_text.split('\n')
    current_pillar = None
    
    for line in lines:
        line = line.strip()
        # Pillars are usually "### 🏛️ Pillar 1: Name"
        if "Pillar" in line and "###" in line:
            # Extract name: Remove ###, Pillar X:, and emojis
            pillar_name = line.replace("###", "").split(":")[-1].strip()
            node_id = f"P_{pillar_name}"
            
            # Pillar Node (Medium Hub)
            nodes.append(Node(id=node_id, label=truncate(pillar_name), title=pillar_name, size=35, color="#1E90FF", font={'size': 18, 'color': 'white', 'face': 'arial'})) 
            edges.append(Edge(source="ROOT", target=node_id, width=3, color="#A9A9A9")) # Thicker edge
            current_pillar = node_id
            
        # Topics are usually "#### 1. Title"
        elif "####" in line and current_pillar:
            # Extract name: Remove ####, 1., etc.
            topic_name = line.replace("####", "").strip()
            # Remove leading numbers like "1. "
            if topic_name[0].isdigit():
                parts = topic_name.split(".", 1)
                if len(parts) > 1:
                    topic_name = parts[1].strip()
            
            node_id = f"T_{topic_name}"
            
            # Logic to determine Green vs Red
            is_gap = True # Default to Red (Gap)
            color = "#FF4B4B" if is_gap else "#00C851" # Red vs Green
            
            # Topic Node (Leaf)
            nodes.append(Node(id=node_id, label=truncate(topic_name), title=topic_name, size=20, color=color, font={'size': 14, 'color': 'white', 'face': 'arial'}))
            edges.append(Edge(source=current_pillar, target=node_id, width=1, color="#D3D3D3"))

    config = Config(
        width=None, 
        height=800, 
        directed=True, 
        physics=True, 
        hierarchical=False,
        node={'labelProperty': 'label', 'renderLabel': True},
        edges={'smooth': False}, 
        physicsOptions={
            "barnesHut": {
                "gravitationalConstant": -10000, 
                "centralGravity": 0.1, 
                "springLength": 250, 
                "springConstant": 0.01,
                "damping": 0.09,
                "avoidOverlap": 1
            },
            "minVelocity": 0.75
        }
    )
    
    # Render Graph
    return_value = agraph(nodes=nodes, edges=edges, config=config)
    
    # 3. Show Roadmap Text
    st.markdown("---")
    st.subheader("📄 Detailed Content Roadmap")
    st.markdown(roadmap_text)
    
    # Word Download
    docx_file = utils.create_docx(roadmap_text)
    st.download_button(
        "📄 Download Roadmap (Word Doc)",
        docx_file,
        "content_roadmap.docx",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    
    if st.button("Reset Analysis"):
        st.session_state['graph_generated'] = False
        st.session_state['roadmap_text'] = ""
        st.rerun()
