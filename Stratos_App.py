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
utils.header("STRATOS: The Strategist (v1.1)", "Visual Intelligence & Roadmap Engine")

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
    
    st.markdown("---")
    strategy_depth = st.select_slider(
        "Strategy Depth (Nodes)",
        options=["Lite (Quick Wins)", "Pro (Balanced)", "Empire (Dominance)"],
        value="Pro (Balanced)",
        help="Lite = Viral Focus (15 nodes). Pro = Authority Focus (30 nodes). Empire = Total Niche Domination (70+ nodes)."
    )
    
    run_btn = st.button("🚀 Initialize Strategy Engine")
    
    st.markdown("---")
    
    # --- SaaS Monetization Logic (Smart Payment Routing) ---
    st.markdown("### 💎 Unlock Full Access")
    
    # 1. Geo-Detection
    # We use a simple try-except block to avoid crashing if the API fails
    user_country = "US" # Default to International
    try:
        import requests
        response = requests.get('https://ipapi.co/json/', timeout=3)
        if response.status_code == 200:
            data = response.json()
            user_country = data.get('country_code', 'US')
    except:
        pass # Fallback to US if offline or API error
        
    # 2. Dynamic Button Rendering
    if user_country == "NG":
        # Nigeria: Paystack (Naira)
        st.info("🇳🇬 **Nigerian Pricing Detected**")
        st.markdown("""
        <a href="https://paystack.com/pay/stratos-ng" target="_blank">
            <button style="width: 100%; background-color: #00C851; color: white; border: none; padding: 10px; border-radius: 5px; font-weight: bold; cursor: pointer;">
                💳 Get Pro Access (₦5,000/mo)
            </button>
        </a>
        """, unsafe_allow_html=True)
    else:
        # Global: Lemon Squeezy (USD)
        st.info(f"🌍 **International Pricing ({user_country})**")
        st.markdown("""
        <a href="https://stratos.lemonsqueezy.com/checkout" target="_blank">
            <button style="width: 100%; background-color: #7047EB; color: white; border: none; padding: 10px; border-radius: 5px; font-weight: bold; cursor: pointer;">
                💳 Get Pro Access ($97/mo)
            </button>
        </a>
        """, unsafe_allow_html=True)

if run_btn and niche and api_key:
    with st.spinner("🕵️ The Strategist is analyzing the web... (This may take 1-2 mins)"):
        # 1. Run the existing text-based strategist
        roadmap_text = strategist.generate_roadmap(niche, user_url, manual_competitors, api_key, strategy_depth)
        
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
            
        # Topics are usually "#### 1. Title" or "#### [OPPORTUNITY] Title"
        elif "####" in line and current_pillar:
            # Extract name: Remove ####
            raw_name = line.replace("####", "").strip()
            
            # Check for Opportunity Tag
            is_opportunity = "[OPPORTUNITY]" in raw_name
            
            # Clean Name
            topic_name = raw_name.replace("[OPPORTUNITY]", "").strip()
            # Remove leading numbers like "1. "
            if topic_name[0].isdigit() and "." in topic_name:
                parts = topic_name.split(".", 1)
                if len(parts) > 1:
                    topic_name = parts[1].strip()
            
            node_id = f"T_{topic_name}"
            
            # Logic to determine Color
            # Opportunity = Gold/Orange (High Demand)
            # Standard = Green (Safe/Standard)
            if is_opportunity:
                color = "#FF8C00" # Dark Orange / Gold
                label = f"🔥 {truncate(topic_name)}"
                size = 25
            else:
                color = "#00C851" # Green
                label = truncate(topic_name)
                size = 20
            
            # Topic Node (Leaf)
            nodes.append(Node(id=node_id, label=label, title=topic_name, size=size, color=color, font={'size': 14, 'color': 'white', 'face': 'arial'}))
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

# Show Impact Metrics on every page load (at the bottom)
utils.display_impact_metrics()
