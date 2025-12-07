import streamlit as st
import utils

utils.load_css()
utils.header("Contact Support", "We are here to help you scale.")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 📬 Get in Touch
    Have a feature request, bug report, or enterprise inquiry?
    
    **Email:** oladeji.lawrence@gmail.com
    **Twitter:** @StratosAI
    **Contact:** Lawrence Oladeji
    """)
    
    st.markdown("### 🌐 Enterprise Solutions")
    st.info("Need a custom version of STRATOS for your agency? We offer white-label solutions with custom API integrations.")

with col2:
    st.markdown("### 💬 Send us a message")
    name = st.text_input("Name")
    email = st.text_input("Email")
    msg = st.text_area("Message")
    if st.button("Send Message"):
        st.success(f"Thanks {name}! We've received your message and will respond to {email} shortly.")

st.markdown("---")
st.markdown("© 2025 STRATOS AI. All Rights Reserved.")
