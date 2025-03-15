import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional
import datetime

# Import our database and schema
from schema import AgentMetadata
from database import JSONDatabase

# Set page configuration
st.set_page_config(
    page_title="AI Agent Hub - Compare Agents",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
db = JSONDatabase()

# Page title
st.title("Compare Agents")

# Get all agents
all_agents = db.get_all_agents()
all_providers = db.get_all_providers()

# Replace the current warning block with this enhanced version
if not all_agents or len(all_agents) < 2:
    st.warning("You need at least two agents to compare. Please add more agents first.")
    
    # Add button to navigate to Agents page
    if st.button("Go to Agents Page"):
        st.switch_page("pages/3_Agents.py")
    
    # Add expandable information about the comparison feature
    with st.expander("About the comparison feature"):
        st.write("""
        The comparison feature allows you to:
        - View agent capabilities side-by-side
        - Compare features, domains, and LLM support
        - Analyze code snippets from different agents
        - Identify strengths and weaknesses of different agents
        
        Add at least two agents using the Agents page to use this feature.
        """)
    
    st.stop()

# Create provider mapping
provider_map = {p.id: p.name for p in all_providers}

# Select agents to compare
st.subheader("Select Agents to Compare")

# Get agent names for selection
agent_options = {agent.id: f"{agent.name} (v{agent.version})" for agent in all_agents}

# Select up to 3 agents to compare
col1, col2, col3 = st.columns(3)

with col1:
    agent1_id = st.selectbox(
        "First Agent",
        options=list(agent_options.keys()),
        format_func=lambda x: agent_options.get(x, "Unknown"),
        key="agent1"
    )

with col2:
    # Filter out the first agent from options
    agent2_options = {k: v for k, v in agent_options.items() if k != agent1_id}
    agent2_id = st.selectbox(
        "Second Agent",
        options=list(agent2_options.keys()),
        format_func=lambda x: agent_options.get(x, "Unknown"),
        key="agent2"
    )

with col3:
    # Filter out first and second agents from options
    agent3_options = {k: v for k, v in agent_options.items() if k not in [agent1_id, agent2_id]}
    agent3_id = st.selectbox(
        "Third Agent (Optional)",
        options=["None"] + list(agent3_options.keys()),
        format_func=lambda x: "None" if x == "None" else agent_options.get(x, "Unknown"),
        key="agent3"
    )

# Get the selected agents
selected_agents = []
if agent1_id:
    agent1 = db.get_agent(agent1_id)
    if agent1:
        selected_agents.append(agent1)

if agent2_id:
    agent2 = db.get_agent(agent2_id)
    if agent2:
        selected_agents.append(agent2)

if agent3_id and agent3_id != "None":
    agent3 = db.get_agent(agent3_id)
    if agent3:
        selected_agents.append(agent3)

if len(selected_agents) < 2:
    st.warning("Please select at least two different agents to compare.")
    st.stop()

# Function to build comparison data
def build_comparison_data(agents):
    """Build comparison data for the selected agents."""
    # Basic information
    basic_info = []
    for agent in agents:
        provider = provider_map.get(agent.provider_id, "Unknown")
        basic_info.append({
            "Name": agent.name,
            "Version": agent.version,
            "Provider": provider,
            "Description": agent.description
        })
    
    # Features comparison
    features = []
    for agent in agents:
        features.append({
            "Name": agent.name,
            "Planning": agent.features.planning.name if agent.features else "Unknown",
            "Tool Use": agent.features.tool_use.name if agent.features else "Unknown",
            "Memory Types": ", ".join([mem.name for mem in agent.features.memory]) if agent.features and agent.features.memory else "None",
            "Multi-Agent": "Yes" if agent.features and agent.features.multi_agent_collaboration else "No",
            "Human-in-Loop": "Yes" if agent.features and agent.features.human_in_the_loop else "No",
            "Autonomous": "Yes" if agent.features and agent.features.autonomous else "No",
            "Reasoning": ", ".join(agent.features.reasoning_frameworks) if agent.features and agent.features.reasoning_frameworks else "None"
        })
    
    # Domains and tags
    domains_tags = []
    for agent in agents:
        domains_tags.append({
            "Name": agent.name,
            "Domains": ", ".join([d.name for d in agent.domains]) if agent.domains else "None",
            "Tags": ", ".join(agent.tags) if agent.tags else "None"
        })
    
    # LLM Support
    llm_support = []
    for agent in agents:
        llm_list = []
        if agent.supported_llms:
            for llm in agent.supported_llms:
                llm_list.append(f"{llm.model_name} ({llm.provider}): {'⭐' * llm.performance_rating}")
        
        llm_support.append({
            "Name": agent.name,
            "LLMs": "<br>".join(llm_list) if llm_list else "None"
        })
    
    # Return all comparison data
    return {
        "basic_info": basic_info,
        "features": features,
        "domains_tags": domains_tags,
        "llm_support": llm_support
    }

# Build comparison data
comparison_data = build_comparison_data(selected_agents)

# Display comparison
st.header("Comparison Results")

# Basic Information
st.subheader("Basic Information")
basic_df = pd.DataFrame(comparison_data["basic_info"])
st.dataframe(basic_df, hide_index=True, use_container_width=True)

# Features
st.subheader("Features")
features_df = pd.DataFrame(comparison_data["features"])
st.dataframe(features_df, hide_index=True, use_container_width=True)

# Domains and Tags
st.subheader("Domains and Tags")
domains_tags_df = pd.DataFrame(comparison_data["domains_tags"])
st.dataframe(domains_tags_df, hide_index=True, use_container_width=True)

# LLM Support
st.subheader("LLM Support")
llm_df = pd.DataFrame(comparison_data["llm_support"])
st.write(llm_df.to_html(escape=False, index=False), unsafe_allow_html=True)

# Visual comparison
st.subheader("Feature Comparison Chart")
st.info("This is a placeholder for a visual comparison. In a complete implementation, you might add a radar chart or other visualization to compare agent capabilities.")

# Code Snippet Comparison
st.subheader("Code Snippet Comparison")
for agent in selected_agents:
    if agent.code_snippets:
        st.write(f"### {agent.name}")
        for snippet in agent.code_snippets:
            with st.expander(f"{snippet.description} ({snippet.language})"):
                st.code(snippet.code, language=snippet.language.lower())
                if snippet.import_requirements:
                    st.write(f"Required imports: {', '.join(snippet.import_requirements)}")
    else:
        st.write(f"### {agent.name}")
        st.write("No code snippets available")