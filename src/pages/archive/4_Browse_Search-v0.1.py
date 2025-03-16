import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional
import datetime

# Import our database and schema
from schema import AgentMetadata, AgentDomain
from database import JSONDatabase

# Set page configuration
st.set_page_config(
    page_title="AI Agent Hub - Browse & Search",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
db = JSONDatabase()

# Page title
st.title("Browse & Search Agents")

# Sidebar filters
st.sidebar.header("Filters")

# Get all agents
all_agents = db.get_all_agents()
all_providers = db.get_all_providers()
all_frameworks = db.get_all_frameworks()

if not all_agents:
    st.info("No agents have been added yet. Please add some agents first.")
    st.stop()

# Create provider mapping
provider_map = {p.id: p.name for p in all_providers}

# Extract unique domains, tags, etc. from all agents
all_domains = set()
all_tags = set()
all_llm_providers = set()
all_reasoning_frameworks = set()

for agent in all_agents:
    if agent.domains:
        for domain in agent.domains:
            all_domains.add(domain.name)
    
    if agent.tags:
        for tag in agent.tags:
            all_tags.add(tag)
    
    if agent.supported_llms:
        for llm in agent.supported_llms:
            all_llm_providers.add(llm.provider)
    
    if agent.features and agent.features.reasoning_frameworks:
        for framework in agent.features.reasoning_frameworks:
            all_reasoning_frameworks.add(framework)

# Filter by provider
provider_filter = st.sidebar.multiselect(
    "Provider",
    options=[p.name for p in all_providers],
    default=[]
)

# Filter by domain
domain_filter = st.sidebar.multiselect(
    "Domain",
    options=sorted(list(all_domains)),
    default=[]
)

# Filter by tag
tag_filter = st.sidebar.multiselect(
    "Tag",
    options=sorted(list(all_tags)),
    default=[]
)

# Filter by LLM provider
llm_filter = st.sidebar.multiselect(
    "LLM Provider",
    options=sorted(list(all_llm_providers)),
    default=[]
)

# Filter by reasoning framework
reasoning_filter = st.sidebar.multiselect(
    "Reasoning Framework",
    options=sorted(list(all_reasoning_frameworks)),
    default=[]
)

# Search by name or description
search_query = st.sidebar.text_input("Search", "")

# Apply filters
filtered_agents = all_agents

if provider_filter:
    provider_ids = [p.id for p in all_providers if p.name in provider_filter]
    filtered_agents = [a for a in filtered_agents if a.provider_id in provider_ids]

if domain_filter:
    filtered_agents = [
        a for a in filtered_agents if 
        a.domains and any(d.name in domain_filter for d in a.domains)
    ]

if tag_filter:
    filtered_agents = [
        a for a in filtered_agents if 
        a.tags and any(tag in tag_filter for tag in a.tags)
    ]

if llm_filter:
    filtered_agents = [
        a for a in filtered_agents if 
        a.supported_llms and any(llm.provider in llm_filter for llm in a.supported_llms)
    ]

if reasoning_filter:
    filtered_agents = [
        a for a in filtered_agents if 
        a.features and a.features.reasoning_frameworks and
        any(framework in reasoning_filter for framework in a.features.reasoning_frameworks)
    ]

if search_query:
    search_query = search_query.lower()
    filtered_agents = [
        a for a in filtered_agents if 
        search_query in a.name.lower() or 
        (a.description and search_query in a.description.lower())
    ]

# Display results
st.subheader(f"Results ({len(filtered_agents)} agents)")

# Sort by name
filtered_agents.sort(key=lambda a: a.name)

# Display as cards in a grid
cols = st.columns(3)
for i, agent in enumerate(filtered_agents):
    with cols[i % 3]:
        with st.container(border=True):
            st.subheader(agent.name)
            st.caption(f"v{agent.version} | {provider_map.get(agent.provider_id, 'Unknown Provider')}")
            
            if agent.description:
                st.markdown(agent.description[:150] + "..." if len(agent.description) > 150 else agent.description)
            
            # Display domains and tags
            domains_str = ", ".join([d.name for d in agent.domains]) if agent.domains else "N/A"
            tags_str = ", ".join(agent.tags) if agent.tags else "N/A"
            
            st.markdown(f"**Domains**: {domains_str}")
            st.markdown(f"**Tags**: {tags_str}")
            
            # Link to agent details
            if st.button("View Details", key=f"view_{agent.id}"):
                st.session_state["selected_agent"] = agent.id
                st.rerun()

# Show detailed view if an agent is selected
if "selected_agent" in st.session_state:
    agent_id = st.session_state["selected_agent"]
    agent = db.get_agent(agent_id)
    
    if agent:
        # Create a modal-like effect with a container
        with st.container(border=True):
            st.subheader(f"{agent.name} (v{agent.version})")
            
            # Close button
            if st.button("Close"):
                st.session_state.pop("selected_agent")
                st.rerun()
            
            # Get provider information
            provider = db.get_provider(agent.provider_id)
            provider_name = provider.name if provider else "Unknown Provider"
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"**Description**: {agent.description}")
                st.markdown(f"**Provider**: {provider_name}")
                
                # Display features
                st.subheader("Features")
                features_cols = st.columns(2)
                with features_cols[0]:
                    st.markdown(f"**Planning**: {agent.features.planning.name}")
                    st.markdown(f"**Tool Use**: {agent.features.tool_use.name}")
                    memory_types = ", ".join([mem.name for mem in agent.features.memory]) if agent.features.memory else "None"
                    st.markdown(f"**Memory Types**: {memory_types}")
                    
                with features_cols[1]:
                    st.markdown(f"**Multi-Agent Collaboration**: {'Yes' if agent.features.multi_agent_collaboration else 'No'}")
                    st.markdown(f"**Human-in-the-Loop**: {'Yes' if agent.features.human_in_the_loop else 'No'}")
                    st.markdown(f"**Autonomous**: {'Yes' if agent.features.autonomous else 'No'}")
                
                # Display reasoning frameworks
                if agent.features.reasoning_frameworks:
                    st.markdown(f"**Reasoning Frameworks**: {', '.join(agent.features.reasoning_frameworks)}")
                
                # Display LLMs
                if agent.supported_llms:
                    st.subheader("Supported LLMs")
                    llm_df = pd.DataFrame([
                        {"Model": llm.model_name, "Provider": llm.provider, "Rating": "⭐" * llm.performance_rating}
                        for llm in agent.supported_llms
                    ])
                    st.dataframe(llm_df, hide_index=True)
                
                # Display domains
                if agent.domains:
                    domains = ", ".join([domain.name for domain in agent.domains])
                    st.markdown(f"**Domains**: {domains}")
                
                # Display tags
                if agent.tags:
                    st.markdown(f"**Tags**: {', '.join(agent.tags)}")
                
                # Display code snippets
                if agent.code_snippets:
                    st.subheader("Code Snippets")
                    for i, snippet in enumerate(agent.code_snippets):
                        with st.expander(f"{snippet.description} ({snippet.language})"):
                            st.code(snippet.code, language=snippet.language.lower())
                            if snippet.import_requirements:
                                st.markdown(f"**Required imports**: {', '.join(snippet.import_requirements)}")
            
            with col2:
                st.markdown(f"**ID**: `{agent.id}`")
                st.markdown(f"**Version**: {agent.version}")
                
                if agent.github_url:
                    st.markdown(f"**GitHub**: [{agent.github_url}]({agent.github_url})")
                if agent.docs_url:
                    st.markdown(f"**Documentation**: [{agent.docs_url}]({agent.docs_url})")
                
                st.markdown(f"**Added**: {agent.created_at.strftime('%Y-%m-%d')}")