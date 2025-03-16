import streamlit as st
import os
import sys

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import seed_data
from database import JSONDatabase

def main():
    """Main entry point for the Streamlit app."""
    # Ensure data directory exists
    os.makedirs("../data", exist_ok=True)
    
    # Seed initial data
    seed_data()
    
    # Set page configuration
    st.set_page_config(
        page_title="AI Agent Hub",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize database
    db = JSONDatabase()
    
    # Display the home page
    st.title("AI Agent Hub")
    st.markdown("""
    Welcome to the AI Agent Hub - a central repository for discovering, comparing, and managing AI agents.
    
    ### Features:
    - Add and manage providers of AI agents (companies and frameworks)
    - Document agent capabilities and requirements
    - Search and filter agents by various criteria
    - Compare agents side-by-side
    
    ### Getting Started:
    1. Add providers using the **Providers** section
    2. Add agent metadata using the **Agents** section
    3. Browse and search for agents in the **Browse & Search** section
    4. Compare multiple agents in the **Compare Agents** section
    
    This application is designed to help you catalog and discover AI agents across different
    platforms and frameworks.
    """)
    
    # Display quick stats
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Providers/Frameworks", len(db.get_all_providers()))
    with col2:
        st.metric("Agents", len(db.get_all_agents()))
    
    # Display some featured providers
    st.subheader("Featured Providers")
    
    # Create three columns for featured providers
    cols = st.columns(3)
    
    # Get all providers
    providers = db.get_all_providers()
    
    # Display up to 3 providers in columns
    for i, provider in enumerate(providers[:3]):
        with cols[i]:
            with st.container(border=True):
                st.subheader(provider.name)
                st.caption(f"Type: {provider.provider_type.value.capitalize()}")
                st.write(provider.description[:150] + "..." if len(provider.description) > 150 else provider.description)
                st.markdown(f"[Learn More]({provider.url})")
    
    # Display some featured agents
    st.subheader("Featured Agents")
    
    # Create three columns for featured agents
    cols = st.columns(3)
    
    # Get all agents
    agents = db.get_all_agents()
    
    # Display up to 3 agents in columns
    for i, agent in enumerate(agents[:3]):
        with cols[i]:
            with st.container(border=True):
                st.subheader(agent.name)
                
                # Get provider if available
                provider_name = "Unknown"
                if agent.provider_id in db.providers:
                    provider_name = db.providers[agent.provider_id].name
                
                st.caption(f"Provider: {provider_name}")
                st.write(agent.description[:150] + "..." if len(agent.description) > 150 else agent.description)
                
                # Display some key features
                st.write(f"Planning: {agent.features.planning.value}")
                st.write(f"Tool Use: {agent.features.tool_use.value}")
                
                # Show domains
                domains = ", ".join([d.value for d in agent.domains])
                st.write(f"Domains: {domains}")

if __name__ == "__main__":
    main()