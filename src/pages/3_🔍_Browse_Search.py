import streamlit as st
import os
import sys

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schema import AgentDomain, PlanningCapability, ToolUseCapability, MemoryType
from database import JSONDatabase
from utils import get_provider_options

# Set page configuration
st.set_page_config(
    page_title="Agent-Search",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
db = JSONDatabase()

# Page title
st.header("🔍 Browse & Search Agents")
st.markdown("""
Find AI agents based on their capabilities, features, and domains. Use the filters on the sidebar to narrow down your search.
""")

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
provider_options = get_provider_options(db, include_none=False)
provider_options["all"] = "All Providers"
filter_provider = st.sidebar.selectbox(
    "Provider", 
    options=["all"] + list(provider_options.keys()),
    format_func=lambda x: provider_options[x] if x != "all" else "All Providers",
    index=0
)

# Domain filter
domain_options = {d.value: d.value for d in AgentDomain}
domain_options["all"] = "All Domains"
filter_domain = st.sidebar.selectbox(
    "Domain", 
    options=list(domain_options.keys()),
    format_func=lambda x: domain_options[x].capitalize() if x != "all" else "All Domains",
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
    format_func=lambda x: planning_options[x].capitalize() if x != "all" else "Any Planning",
    index=list(planning_options.keys()).index("all")
)

# Tool use capability filter
tool_use_options = {t.value: t.value for t in ToolUseCapability}
tool_use_options["all"] = "Any Tool Use"
filter_tool_use = st.sidebar.selectbox(
    "Tool Use Capability", 
    options=list(tool_use_options.keys()),
    format_func=lambda x: tool_use_options[x].capitalize() if x != "all" else "Any Tool Use",
    index=list(tool_use_options.keys()).index("all")
)

# Memory type filter
memory_options = {m.value: m.value for m in MemoryType}
memory_options["all"] = "Any Memory Type"
filter_memory = st.sidebar.selectbox(
    "Memory Type", 
    options=list(memory_options.keys()),
    format_func=lambda x: memory_options[x].capitalize() if x != "all" else "Any Memory Type",
    index=list(memory_options.keys()).index("all")
)

# Boolean feature filters
st.sidebar.subheader("Additional Features")
filter_multi_agent = st.sidebar.checkbox("Multi-agent Collaboration")
filter_human_in_loop = st.sidebar.checkbox("Human-in-the-loop")
filter_autonomous = st.sidebar.checkbox("Autonomous")
filter_vision = st.sidebar.checkbox("Vision Support")
filter_audio = st.sidebar.checkbox("Audio Support")

# Tag filter
st.sidebar.subheader("Tags")
all_tags = set()
for agent in agents:
    all_tags.update(agent.tags)

if all_tags:
    selected_tags = st.sidebar.multiselect(
        "Filter by Tags",
        options=sorted(all_tags)
    )
else:
    selected_tags = []

# Display options
st.sidebar.subheader("Display Options")
display_mode = st.sidebar.radio(
    "View as",
    options=["Cards", "Compact List"],
    horizontal=True
)

# Main content area
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

# Tag filter
if selected_tags:
    filtered_agents = [
        agent for agent in filtered_agents 
        if any(tag in agent.tags for tag in selected_tags)
    ]

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
col1, col2 = st.columns([3, 1])
with col1:
    st.subheader(f"Results ({len(filtered_agents)} agents)")
with col2:
    # Add option to sort
    sort_option = st.selectbox(
        "Sort by",
        options=["Name", "Provider", "Updated Date"],
        index=0
    )
    
    # Apply sorting
    if sort_option == "Name":
        filtered_agents = sorted(filtered_agents, key=lambda a: a.name)
    elif sort_option == "Provider":
        filtered_agents = sorted(filtered_agents, key=lambda a: provider_dict.get(a.provider_id, "").name if a.provider_id else "")
    elif sort_option == "Updated Date":
        filtered_agents = sorted(filtered_agents, key=lambda a: a.updated_at, reverse=True)

if not filtered_agents:
    st.info("No agents match the current filters. Try adjusting your search criteria.")
else:
    if display_mode == "Cards":
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
                    
                    st.write(f"**Provider**: {provider_name}")
                    
                    # Description - truncated
                    desc = agent.description
                    if len(desc) > 100:
                        desc = desc[:100] + "..."
                    st.write(desc)
                    
                    # Domains
                    domains_str = ", ".join([d.value for d in agent.domains])
                    st.write(f"**Domains**: {domains_str}")
                    
                    # Key features
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Planning**: {agent.features.planning.value}")
                    with col2:
                        st.write(f"**Tool Use**: {agent.features.tool_use.value}")
                    
                    # Tags (if any)
                    if agent.tags:
                        st.write(f"**Tags**: {', '.join(agent.tags)}")
                    
                    # View details button
                    if st.button("View Details", key=f"view_{agent.id}"):
                        st.session_state["selected_agent"] = agent.id
                        st.rerun()
    else:  # Compact List
        for agent in filtered_agents:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{agent.name}** (v{agent.version})")
                    
                    # Provider and domains
                    provider_name = "Unknown"
                    if agent.provider_id in provider_dict:
                        provider_name = provider_dict[agent.provider_id].name
                    
                    domains_str = ", ".join([d.value for d in agent.domains])
                    st.write(f"**Provider**: {provider_name} | **Domains**: {domains_str}")
                    
                    # Key features - compressed
                    features = []
                    features.append(f"Planning: {agent.features.planning.value}")
                    features.append(f"Tool Use: {agent.features.tool_use.value}")
                    
                    if agent.features.multi_agent_collaboration:
                        features.append("Multi-agent")
                    if agent.features.human_in_the_loop:
                        features.append("Human-in-loop")
                    if agent.features.autonomous:
                        features.append("Autonomous")
                    
                    st.write(f"**Features**: {' • '.join(features)}")
                
                with col2:
                    st.write(f"**Updated**: {agent.updated_at.strftime('%Y-%m-%d')}")
                    if st.button("View", key=f"view_compact_{agent.id}"):
                        st.session_state["selected_agent"] = agent.id
                        st.rerun()

# Agent details section
if "selected_agent" in st.session_state:
    agent_id = st.session_state["selected_agent"]
    agent = db.get_agent(agent_id)
    
    if agent:
        detail_container = st.container()
        
        with detail_container:
            st.header(f"Agent Details: {agent.name}")
            
            # Clear selection button
            if st.button("← Back to Results"):
                st.session_state.pop("selected_agent")
                st.rerun()
            
            st.caption(f"Version: {agent.version}")
            
            # Create tabs for different sections of the agent details
            detail_tabs = st.tabs([
                "Basic Info", 
                "Features", 
                "Resources", 
                "LLM Support", 
                "Code Snippets"
            ])
            
            # Tab 1: Basic Information
            with detail_tabs[0]:
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
                    links = []
                    if agent.github_url:
                        links.append(f"[GitHub Repository]({agent.github_url})")
                    if agent.docs_url:
                        links.append(f"[Documentation]({agent.docs_url})")
                    if agent.demo_url:
                        links.append(f"[Live Demo]({agent.demo_url})")
                    
                    if links:
                        st.markdown("**Links**:")
                        for link in links:
                            st.markdown(link)
                    
                    st.markdown(f"**Added**: {agent.created_at.strftime('%Y-%m-%d')}")
                    st.markdown(f"**Updated**: {agent.updated_at.strftime('%Y-%m-%d')}")
                    
                    # Actions
                    if st.button("Edit Agent", key="edit_agent_btn"):
                        # Set the agent_id in session state for the Agents page
                        st.session_state["selected_agent_id"] = agent.id
                        # Navigate to the Agents page
                        st.switch_page("pages/2_🤖_Agents.py")
            
            # Tab 2: Features
            with detail_tabs[1]:
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
            
            # Tab 3: Resource Requirements
            with detail_tabs[2]:
                if hasattr(agent, 'resource_requirements') and agent.resource_requirements:
                    reqs = agent.resource_requirements
                    
                    # Only show content if there's at least one field populated
                    if any([
                        reqs.min_cpu, reqs.recommended_cpu, reqs.min_ram, 
                        reqs.recommended_ram, reqs.gpu_required, reqs.recommended_gpu,
                        reqs.estimated_cost_per_hour, reqs.notes
                    ]):
                        res_col1, res_col2 = st.columns(2)
                        
                        with res_col1:
                            if reqs.min_cpu:
                                st.markdown(f"**Min CPU**: {reqs.min_cpu}")
                            if reqs.min_ram:
                                st.markdown(f"**Min RAM**: {reqs.min_ram}")
                            if reqs.gpu_required:
                                st.markdown("**GPU Required**: Yes")
                                if reqs.recommended_gpu:
                                    st.markdown(f"**Recommended GPU**: {reqs.recommended_gpu}")
                        
                        with res_col2:
                            if reqs.recommended_cpu:
                                st.markdown(f"**Recommended CPU**: {reqs.recommended_cpu}")
                            if reqs.recommended_ram:
                                st.markdown(f"**Recommended RAM**: {reqs.recommended_ram}")
                            if reqs.estimated_cost_per_hour:
                                st.markdown(f"**Est. Cost/Hour**: ${reqs.estimated_cost_per_hour:.2f}")
                        
                        if reqs.notes:
                            st.markdown(f"**Notes**: {reqs.notes}")
                    else:
                        st.info("No resource requirements specified for this agent.")
                else:
                    st.info("No resource requirements specified for this agent.")
            
            # Tab 4: LLM Support
            with detail_tabs[3]:
                if agent.supported_llms:
                    # Create a layout with 2 LLMs per row
                    for i in range(0, len(agent.supported_llms), 2):
                        cols = st.columns(2)
                        for j in range(2):
                            if i + j < len(agent.supported_llms):
                                llm = agent.supported_llms[i + j]
                                with cols[j]:
                                    with st.container(border=True):
                                        st.markdown(f"**{llm.model_name}**")
                                        
                                        # Provider
                                        provider_info = ""
                                        if hasattr(llm, 'provider') and llm.provider:
                                            provider_info = f"Provider: {llm.provider.name}" if llm.provider.name else ""
                                        elif hasattr(llm, 'provider_id') and llm.provider_id:
                                            provider = provider_dict.get(llm.provider_id)
                                            if provider:
                                                provider_info = f"Provider: {provider.name}"
                                        
                                        if provider_info:
                                            st.markdown(provider_info)
                                        
                                        if llm.min_version:
                                            st.markdown(f"Min Version: {llm.min_version}")
                                        if llm.performance_rating:
                                            st.markdown(f"Rating: {'⭐' * llm.performance_rating}")
                                        if llm.notes:
                                            st.markdown(f"Notes: {llm.notes}")
                else:
                    st.info("No LLM support information available for this agent.")
            
            # Tab 5: Code Snippets
            with detail_tabs[4]:
                if agent.code_snippets:
                    # Use containers instead of expanders to avoid nesting issues
                    for i, snippet in enumerate(agent.code_snippets):
                        with st.container(border=True):
                            st.markdown(f"### {snippet.description} ({snippet.language})")
                            st.code(snippet.code, language=snippet.language)
                            if snippet.import_requirements:
                                st.markdown(f"**Requirements**: {', '.join(snippet.import_requirements)}")
                else:
                    st.info("No code snippets available for this agent.")
            
            # Compare button at the bottom of the details
            st.button("Compare with other agents", on_click=lambda: st.switch_page("pages/4_📊_Compare_Agents.py"))