import streamlit as st
import os
from database import JSONDatabase

# Import seed_data function from previous main.py
from app import seed_data

def main():
    """Main function for the home page"""
    # Initialize database
    db = JSONDatabase()
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Set page configuration
    st.set_page_config(
        page_title="AI Agent Hub",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Home page content
    st.header("AI Agent Hub")
    st.markdown("""
    Welcome to the AI Agent Hub - a central repository for discovering, comparing, and managing AI agents.
    
    ### Features:
    - Add and manage providers of AI agents
    - Catalog agent frameworks
    - Document agent capabilities and requirements
    - Search and filter agents by various criteria
    - Compare agents side-by-side
    
    ### Getting Started:
    1. Add providers of AI agents using the **Providers** section
    2. Document frameworks using the **Frameworks** section
    3. Add agent metadata using the **Agents** section
    4. Browse and search for agents in the **Browse & Search** section
    5. Compare multiple agents in the **Compare Agents** section
    
    This application is designed to help you catalog and discover AI agents across different
    platforms and frameworks.
    """)
    
    # Display quick stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Providers", len(db.get_all_providers()))
    with col2:
        st.metric("Frameworks", len(db.get_all_frameworks()))
    with col3:
        st.metric("Agents", len(db.get_all_agents()))

if __name__ == "__main__":
    # Seed initial data
    seed_data()
    
    # Run the home page
    main()