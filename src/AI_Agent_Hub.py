import streamlit as st
import os
import sys

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import seed_data
from database import JSONDatabase
from schema import ProviderType

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
    provider_counts = {}
    for provider in db.get_all_providers():
        provider_type = provider.provider_type.value
        provider_counts[provider_type] = provider_counts.get(provider_type, 0) + 1
    
    # Create a metric for total providers and a breakdown by type
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Providers", len(db.get_all_providers()))
        
        # Show provider breakdown if there are any providers
        if provider_counts:
            st.caption("Provider Types:")
            for ptype, count in provider_counts.items():
                st.caption(f"- {ptype.capitalize()}: {count}")
    
    with col2:
        st.metric("Agents", len(db.get_all_agents()))
        
        # Show agent domain breakdown if there are any agents
        if db.get_all_agents():
            # Count agents by domain
            domain_counts = {}
            for agent in db.get_all_agents():
                for domain in agent.domains:
                    domain_name = domain.value
                    domain_counts[domain_name] = domain_counts.get(domain_name, 0) + 1
            
            # Display domain counts
            st.caption("Agent Domains:")
            # Show top 3 domains at most
            for domain, count in list(sorted(domain_counts.items(), key=lambda x: x[1], reverse=True))[:3]:
                st.caption(f"- {domain.capitalize()}: {count}")
    
    # Display some featured providers
    st.subheader("Featured Providers")
    
    # Create columns for featured providers
    provider_cols = st.columns(3)
    
    # Get providers by different types for a balanced display
    companies = db.get_providers_by_type(ProviderType.COMPANY)[:1]
    frameworks = db.get_providers_by_type(ProviderType.FRAMEWORK)[:1]
    open_source = db.get_providers_by_type(ProviderType.OPEN_SOURCE)[:1]
    
    # Combine providers ensuring we have at most 3
    featured_providers = companies + frameworks + open_source
    featured_providers = featured_providers[:3]
    
    # Display featured providers
    for i, provider in enumerate(featured_providers):
        with provider_cols[i]:
            with st.container(border=True):
                st.subheader(provider.name)
                st.caption(f"Type: {provider.provider_type.value.capitalize()}")
                description = provider.description
                if len(description) > 150:
                    description = description[:150] + "..."
                st.write(description)
                
                # Add links
                links = []
                if provider.url:
                    links.append(f"[Website]({provider.url})")
                if provider.github_url:
                    links.append(f"[GitHub]({provider.github_url})")
                if provider.docs_url:
                    links.append(f"[Docs]({provider.docs_url})")
                    
                st.write(" | ".join(links))
    
    # Display some featured agents
    st.subheader("Featured Agents")
    
    # Create columns for featured agents
    agent_cols = st.columns(3)
    
    # Get all agents
    agents = db.get_all_agents()
    
    # Display up to 3 agents in columns
    for i, agent in enumerate(agents[:3]):
        with agent_cols[i]:
            with st.container(border=True):
                st.subheader(agent.name)
                
                # Get provider if available
                provider_name = "Unknown"
                provider_type = ""
                if agent.provider:
                    provider_name = agent.provider.name
                    provider_type = f" ({agent.provider.provider_type.value})"
                
                st.caption(f"Provider: {provider_name}{provider_type}")
                
                # Description
                description = agent.description
                if len(description) > 120:
                    description = description[:120] + "..."
                st.write(description)
                
                # Display some key features
                features_col1, features_col2 = st.columns(2)
                with features_col1:
                    st.write(f"**Planning:** {agent.features.planning.value}")
                    st.write(f"**Tool Use:** {agent.features.tool_use.value}")
                
                with features_col2:
                    # Get LLM support
                    llms = []
                    for llm in agent.supported_llms[:2]:  # Show max 2 LLMs
                        provider_name = llm.provider.name if llm.provider else "Unknown"
                        llms.append(f"{llm.model_name} ({provider_name})")
                    
                    if llms:
                        st.write("**LLMs:**")
                        for llm in llms:
                            st.write(f"- {llm}")
                
                # Show domains
                st.write("**Domains:**")
                domains_text = ", ".join([d.value for d in agent.domains])
                st.write(domains_text)
                
                # Add a View Details button
                if st.button("View Details", key=f"view_{agent.id}"):
                    # Store the selected agent ID in session state
                    st.session_state["selected_agent_id"] = agent.id
                    # Redirect to the Agents page
                    st.switch_page("pages/3_🤖_Agents.py")
                


if __name__ == "__main__":
    main()