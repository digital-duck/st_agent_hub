import streamlit as st
import os
import sys

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schema import AgentDomain, PlanningCapability, ToolUseCapability, MemoryType
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

# Get all data
agents = db.get_all_agents()
providers = db.get_all_providers()

if not agents:
    st.info("No agents added yet. Go to the Agents section to add some.")
    st.stop()

# Convert to dictionaries for easier lookups
provider_dict = {p.id: p for p in providers}

# Sidebar filters
st.sidebar.header("Filters")

# Provider filter
provider_options = {p.id: f"{p.name} ({p.provider_type.value})" for p in providers}
provider_options["all"] = "All Providers"
filter_provider = st.sidebar.selectbox(
    "Provider", 
    options=list(provider_options.keys()),
    format_func=lambda x: provider_options[x],
    index=list(provider_options.keys()).index("all")
)

# Domain filter
domain_options = {d.value: d.value for d in AgentDomain}
domain_options["all"] = "All Domains"
filter_domain = st.sidebar.selectbox(
    "Domain", 
    options=list(domain_options.keys()),
    format_func=lambda x: domain_options[x],
    index=list(domain_options.keys()).index("all")
)

# Feature filters
st.sidebar.subheader("Features")

# Planning capability filter
planning_options = {p.value: p.value for p in PlanningCapability}
planning_options["all"] = "Any Planning"
filter_planning = st.sidebar.selectbox(
    "Planning Capability", 
    options=list(planning_options.keys()),
    format_func=lambda x: planning_options[x],
    index=list(planning_options.keys()).index("all")
)

# Tool use capability filter
tool_use_options = {t.value: t.value for t in ToolUseCapability}
tool_use_options["all"] = "Any Tool Use"
filter_tool_use = st.sidebar.selectbox(
    "Tool Use Capability", 
    options=list(tool_use_options.keys()),
    format_func=lambda x: tool_use_options[x],
    index=list(tool_use_options.keys()).index("all")
)

# Memory type filter
memory_options = {m.value: m.value for m in MemoryType}
memory_options["all"] = "Any Memory Type"
filter_memory = st.sidebar.selectbox(
    "Memory Type", 
    options=list(memory_options.keys()),
    format_func=lambda x: memory_options[x],
    index=list(memory_options.keys()).index("all")
)

# Boolean feature filters
filter_multi_agent = st.sidebar.checkbox("Multi-agent Collaboration")
filter_human_in_loop = st.sidebar.checkbox("Human-in-the-loop")
filter_autonomous = st.sidebar.checkbox("Autonomous")
filter_vision = st.sidebar.checkbox("Vision Support")
filter_audio = st.sidebar.checkbox("Audio Support")

# Search box
search_query = st.text_input("Search Agents", placeholder="Enter name, description, or tags...")

# Apply filters
filtered_agents = agents

# Provider filter
if filter_provider != "all":
    filtered_agents = [agent for agent in filtered_agents if agent.provider_id == filter_provider]

# Domain filter
if filter_domain != "all":
    filtered_agents = [agent for agent in filtered_agents if any(d.value == filter_domain for d in agent.domains)]

# Planning capability filter
if filter_planning != "all":
    filtered_agents = [agent for agent in filtered_agents if agent.features.planning.value == filter_planning]

# Tool use capability filter
if filter_tool_use != "all":
    filtered_agents = [agent for agent in filtered_agents if agent.features.tool_use.value == filter_tool_use]

# Memory type filter
if filter_memory != "all":
    filtered_agents = [agent for agent in filtered_agents if any(m.value == filter_memory for m in agent.features.memory)]

# Boolean feature filters
if filter_multi_agent:
    filtered_agents = [agent for agent in filtered_agents if agent.features.multi_agent_collaboration]

if filter_human_in_loop:
    filtered_agents = [agent for agent in filtered_agents if agent.features.human_in_the_loop]

if filter_autonomous:
    filtered_agents = [agent for agent in filtered_agents if agent.features.autonomous]

if filter_vision:
    filtered_agents = [agent for agent in filtered_agents if agent.features.supports_vision]

if filter_audio:
    filtered_agents = [agent for agent in filtered_agents if agent.features.supports_audio]

# Search query
if search_query:
    query = search_query.lower()
    filtered_agents = [
        agent for agent in filtered_agents 
        if query in agent.name.lower() 
        or query in agent.description.lower()
        or any(query in tag.lower() for tag in agent.tags)
    ]

# Display results
st.subheader(f"Results ({len(filtered_agents)} agents)")

if not filtered_agents:
    st.info("No agents match the current filters.")
else:
    # Agent cards
    cols = st.columns(3)
    for i, agent in enumerate(filtered_agents):
        col = cols[i % 3]
        with col:
            with st.container(border=True):
                st.subheader(agent.name)
                st.caption(f"v{agent.version}")
                
                # Provider
                provider_name = "Unknown"
                if agent.provider_id in provider_dict:
                    provider_name = provider_dict[agent.provider_id].name
                
                st.write(f"Provider: {provider_name}")
                
                # Description - truncated
                desc = agent.description
                if len(desc) > 100:
                    desc = desc[:100] + "..."
                st.write(desc)
                
                # Domains
                domains_str = ", ".join([d.value for d in agent.domains])
                st.write(f"Domains: {domains_str}")
                
                # Key features
                st.write(f"Planning: {agent.features.planning.value}")
                st.write(f"Tool Use: {agent.features.tool_use.value}")
                
                # View details button
                if st.button("View Details", key=f"view_{agent.id}"):
                    st.session_state["selected_agent"] = agent.id
                    st.rerun()

# Agent details
if "selected_agent" in st.session_state:
    agent_id = st.session_state["selected_agent"]
    agent = db.get_agent(agent_id)
    
    if agent:
        with st.expander("Agent Details", expanded=True):
            # Clear selection button
            if st.button("Back to Results"):
                st.session_state.pop("selected_agent")
                st.rerun()
            
            st.title(agent.name)
            st.caption(f"Version: {agent.version}")
            
            # Basic info
            st.markdown("## Basic Information")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Description**: {agent.description}")
                
                # Provider
                provider = provider_dict.get(agent.provider_id)
                if provider:
                    st.markdown(f"**Provider**: [{provider.name}]({provider.url}) ({provider.provider_type.value})")
                
                # Domains
                st.markdown("**Domains**:")
                domains_str = ", ".join([d.value for d in agent.domains])
                st.write(domains_str)
                
                # Tags
                if agent.tags:
                    st.markdown("**Tags**:")
                    tags_str = ", ".join(agent.tags)
                    st.write(tags_str)
            
            with col2:
                # URLs
                if agent.github_url:
                    st.markdown(f"[GitHub Repository]({agent.github_url})")
                if agent.docs_url:
                    st.markdown(f"[Documentation]({agent.docs_url})")
                if agent.demo_url:
                    st.markdown(f"[Live Demo]({agent.demo_url})")
                
                st.markdown(f"**Added**: {agent.created_at.strftime('%Y-%m-%d')}")
                st.markdown(f"**Updated**: {agent.updated_at.strftime('%Y-%m-%d')}")
            
            # Features
            st.markdown("## Features")
            
            feature_col1, feature_col2 = st.columns(2)
            
            with feature_col1:
                st.markdown(f"**Planning**: {agent.features.planning.value}")
                st.markdown(f"**Tool Use**: {agent.features.tool_use.value}")
                st.markdown("**Memory Types**:")
                for memory_type in agent.features.memory:
                    st.markdown(f"- {memory_type.value}")
                
                if agent.features.reasoning_frameworks:
                    st.markdown("**Reasoning Frameworks**:")
                    for rf in agent.features.reasoning_frameworks:
                        st.markdown(f"- {rf}")
            
            with feature_col2:
                features = []
                if agent.features.multi_agent_collaboration:
                    features.append("Multi-agent Collaboration")
                if agent.features.human_in_the_loop:
                    features.append("Human-in-the-loop")
                if agent.features.autonomous:
                    features.append("Autonomous")
                if agent.features.fine_tuning_support:
                    features.append("Fine-tuning Support")
                if agent.features.streaming_support:
                    features.append("Streaming Support")
                if agent.features.supports_vision:
                    features.append("Vision Support")
                if agent.features.supports_audio:
                    features.append("Audio Support")
                
                if features:
                    st.markdown("**Additional Features**:")
                    for feature in features:
                        st.markdown(f"- {feature}")
            
            # LLM Support
            if agent.supported_llms:
                st.markdown("## Supported LLMs")
                
                for llm in agent.supported_llms:
                    with st.container(border=True):
                        st.markdown(f"**{llm.model_name}** ({llm.provider})")
                        if llm.min_version:
                            st.markdown(f"Min Version: {llm.min_version}")
                        if llm.performance_rating:
                            st.markdown(f"Rating: {'⭐' * llm.performance_rating}")
                        if llm.notes:
                            st.markdown(f"Notes: {llm.notes}")
            
            # Code Snippets
            if agent.code_snippets:
                st.markdown("## Code Snippets")
                
                for snippet in agent.code_snippets:
                    with st.expander(f"{snippet.description} ({snippet.language})"):
                        st.code(snippet.code, language=snippet.language)
                        if snippet.import_requirements:
                            st.markdown(f"**Requirements**: {', '.join(snippet.import_requirements)}")