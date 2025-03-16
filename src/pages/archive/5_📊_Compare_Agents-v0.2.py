import streamlit as st
import pandas as pd
import os
import sys

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
agents = db.get_all_agents()
providers = db.get_all_providers()

if not agents:
    st.info("No agents added yet. Go to the Agents section to add some.")
    st.stop()

if len(agents) < 2:
    st.warning("You need at least 2 agents to compare. Please add more agents.")
    st.stop()

# Convert to dictionaries for easier lookups
provider_dict = {p.id: p for p in providers}

# Select agents to compare
agent_options = {agent.id: f"{agent.name} (v{agent.version})" for agent in agents}

st.write("Select agents to compare (2-4):")

col1, col2 = st.columns(2)

with col1:
    agent1 = st.selectbox("Agent 1", options=list(agent_options.keys()), format_func=lambda x: agent_options[x], key="agent1")

with col2:
    agent2 = st.selectbox("Agent 2", options=list(agent_options.keys()), format_func=lambda x: agent_options[x], key="agent2")

show_agent3 = st.checkbox("Add third agent")
if show_agent3:
    agent3 = st.selectbox("Agent 3", options=list(agent_options.keys()), format_func=lambda x: agent_options[x], key="agent3")
else:
    agent3 = None

show_agent4 = st.checkbox("Add fourth agent")
if show_agent4 and show_agent3:
    agent4 = st.selectbox("Agent 4", options=list(agent_options.keys()), format_func=lambda x: agent_options[x], key="agent4")
else:
    agent4 = None

# Get selected agents
selected_agent_ids = [agent1, agent2]
if agent3:
    selected_agent_ids.append(agent3)
if agent4:
    selected_agent_ids.append(agent4)

# Remove duplicates
selected_agent_ids = list(dict.fromkeys(selected_agent_ids))

if len(selected_agent_ids) < 2:
    st.warning("Please select at least 2 different agents to compare.")
    st.stop()

selected_agents = [next(agent for agent in agents if agent.id == agent_id) for agent_id in selected_agent_ids]

# Compare button
if st.button("Compare Agents"):
    st.subheader("Comparison Results")
    
    # Basic Information
    st.markdown("### Basic Information")
    
    basic_data = []
    for agent in selected_agents:
        provider_name = provider_dict[agent.provider_id].name if agent.provider_id in provider_dict else "N/A"
        provider_type = provider_dict[agent.provider_id].provider_type.value if agent.provider_id in provider_dict else "N/A"
        domains = ", ".join([d.value for d in agent.domains])
        
        basic_data.append({
            "Agent": agent.name,
            "Version": agent.version,
            "Provider": f"{provider_name} ({provider_type})",
            "Domains": domains
        })
    
    st.table(pd.DataFrame(basic_data))
    
    # Features Comparison
    st.markdown("### Features")
    
    feature_data = []
    for agent in selected_agents:
        features = agent.features
        memory_types = ", ".join([m.value for m in features.memory])
        reasoning = ", ".join(features.reasoning_frameworks) if features.reasoning_frameworks else "N/A"
        
        feature_data.append({
            "Agent": agent.name,
            "Planning": features.planning.value,
            "Tool Use": features.tool_use.value,
            "Memory Types": memory_types,
            "Multi-agent": "✓" if features.multi_agent_collaboration else "✗",
            "Human-in-loop": "✓" if features.human_in_the_loop else "✗",
            "Autonomous": "✓" if features.autonomous else "✗",
            "Fine-tuning": "✓" if features.fine_tuning_support else "✗",
            "Streaming": "✓" if features.streaming_support else "✗",
            "Vision": "✓" if features.supports_vision else "✗",
            "Audio": "✓" if features.supports_audio else "✗",
            "Reasoning": reasoning
        })
    
    st.table(pd.DataFrame(feature_data))
    
    # LLM Support
    st.markdown("### LLM Support")
    
    # Create a set of all unique LLM providers
    all_llms = set()
    for agent in selected_agents:
        for llm in agent.supported_llms:
            all_llms.add(f"{llm.model_name} ({llm.provider})")
    
    if all_llms:
        llm_data = []
        for agent in selected_agents:
            agent_llms = {f"{llm.model_name} ({llm.provider})": "✓" for llm in agent.supported_llms}
            
            row = {"Agent": agent.name}
            for llm in sorted(all_llms):
                row[llm] = agent_llms.get(llm, "✗")
            
            llm_data.append(row)
        
        st.table(pd.DataFrame(llm_data))
    else:
        st.info("No LLM support information available for these agents.")
    
    # Code snippets comparison
    st.markdown("### Code Snippets")
    
    for agent in selected_agents:
        if agent.code_snippets:
            st.write(f"#### {agent.name}")
            for snippet in agent.code_snippets:
                with st.expander(f"{snippet.description} ({snippet.language})"):
                    st.code(snippet.code, language=snippet.language)
                    if snippet.import_requirements:
                        st.markdown(f"**Requirements**: {', '.join(snippet.import_requirements)}")
        else:
            st.write(f"#### {agent.name}")
            st.info("No code snippets available for this agent.")