import streamlit as st
import pandas as pd
import os
import sys

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import JSONDatabase
from app import get_provider_options

# Set page configuration
st.set_page_config(
    page_title="AI Agent Hub - Compare Agents",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
db = JSONDatabase()

# Page title
st.title("📊 Compare Agents")
st.markdown("""
Compare different AI agents side-by-side to see their strengths, capabilities, and features.
Select up to 4 agents to compare them across different dimensions.
""")

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

# Handle pre-selected agent from Browse & Search page
preselected_agent = st.session_state.get("selected_agent")

# Organize agents by provider for easier selection
providers_with_agents = {}
for agent in agents:
    provider_id = agent.provider_id
    provider_name = provider_dict.get(provider_id, "Unknown").name if provider_id else "Unknown"
    
    if provider_name not in providers_with_agents:
        providers_with_agents[provider_name] = []
    
    providers_with_agents[provider_name].append(agent)

# Select agents to compare
st.subheader("Select Agents to Compare")

# Create tabs for each provider
provider_tabs = st.tabs(list(providers_with_agents.keys()) + ["All Agents"])

# Track selected agents across tabs
if "compare_selected_agents" not in st.session_state:
    st.session_state.compare_selected_agents = set()
    # Add preselected agent if it exists
    if preselected_agent:
        st.session_state.compare_selected_agents.add(preselected_agent)
        # Clear it after using it
        st.session_state.pop("selected_agent", None)

# Display agents for each provider in tabs
for i, (provider_name, provider_agents) in enumerate(providers_with_agents.items()):
    with provider_tabs[i]:
        st.write(f"Select agents from {provider_name}:")
        
        # Create 2 columns for agent selection
        cols = st.columns(2)
        for j, agent in enumerate(provider_agents):
            col = cols[j % 2]
            with col:
                is_selected = agent.id in st.session_state.compare_selected_agents
                if st.checkbox(
                    f"{agent.name} (v{agent.version})", 
                    value=is_selected,
                    key=f"provider_{provider_name}_agent_{agent.id}"
                ):
                    st.session_state.compare_selected_agents.add(agent.id)
                else:
                    if agent.id in st.session_state.compare_selected_agents:
                        st.session_state.compare_selected_agents.remove(agent.id)

# All agents tab
with provider_tabs[-1]:
    st.write("Select from all available agents:")
    
    # Create 3 columns for agent selection
    cols = st.columns(3)
    for j, agent in enumerate(agents):
        col = cols[j % 3]
        with col:
            provider_name = provider_dict.get(agent.provider_id, "Unknown").name if agent.provider_id else "Unknown"
            is_selected = agent.id in st.session_state.compare_selected_agents
            if st.checkbox(
                f"{agent.name} (v{agent.version}) - {provider_name}", 
                value=is_selected,
                key=f"all_agent_{agent.id}"
            ):
                st.session_state.compare_selected_agents.add(agent.id)
            else:
                if agent.id in st.session_state.compare_selected_agents:
                    st.session_state.compare_selected_agents.remove(agent.id)

# Display selected agents
st.subheader("Selected Agents")

# Get the agent objects for selected IDs
selected_agent_ids = list(st.session_state.compare_selected_agents)
selected_agents = [next((a for a in agents if a.id == agent_id), None) for agent_id in selected_agent_ids]
selected_agents = [a for a in selected_agents if a]  # Remove None values

if len(selected_agents) < 2:
    st.warning("Please select at least 2 agents to compare.")
else:
    # Display selected agents as pills
    cols = st.columns(len(selected_agents))
    for i, agent in enumerate(selected_agents):
        with cols[i]:
            st.markdown(f"**{i+1}. {agent.name}**")
            provider_name = provider_dict.get(agent.provider_id, "Unknown").name if agent.provider_id else "Unknown"
            st.caption(f"{provider_name} • v{agent.version}")
    
    # Compare agents button
    if st.button("Compare Selected Agents", type="primary"):
        st.session_state["show_comparison"] = True
    
    # Clear selection button
    if st.button("Clear Selection"):
        st.session_state.compare_selected_agents = set()
        if "show_comparison" in st.session_state:
            st.session_state.pop("show_comparison")
        st.rerun()

# Show comparison results
if "show_comparison" in st.session_state and selected_agents and len(selected_agents) >= 2:
    st.markdown("---")
    st.header("Comparison Results")
    
    # Create tabs for different comparison categories
    tab1, tab2, tab3, tab4 = st.tabs(["Basic Information", "Features", "LLM Support", "Code Snippets"])
    
    with tab1:
        # Basic Information Comparison
        st.subheader("Basic Information")
        
        basic_data = []
        for agent in selected_agents:
            provider_name = "Unknown"
            provider_type = "Unknown"
            if agent.provider_id in provider_dict:
                provider = provider_dict[agent.provider_id]
                provider_name = provider.name
                provider_type = provider.provider_type.value
            
            domains = ", ".join([d.value for d in agent.domains])
            tags = ", ".join(agent.tags) if agent.tags else "N/A"
            
            basic_data.append({
                "Agent": agent.name,
                "Version": agent.version,
                "Provider": f"{provider_name} ({provider_type})",
                "Domains": domains,
                "Tags": tags
            })
        
        # Convert to DataFrame and display
        basic_df = pd.DataFrame(basic_data)
        st.dataframe(
            basic_df,
            hide_index=True,
            use_container_width=True
        )
        
        # Description comparison
        st.subheader("Descriptions")
        
        for i, agent in enumerate(selected_agents):
            with st.container(border=True):
                st.write(f"**{agent.name}**")
                st.write(agent.description)
    
    with tab2:
        # Features Comparison
        st.subheader("Features")
        
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
                "Multi-agent": "Yes" if features.multi_agent_collaboration else "No",
                "Human-in-loop": "Yes" if features.human_in_the_loop else "No",
                "Autonomous": "Yes" if features.autonomous else "No",
                "Fine-tuning": "Yes" if features.fine_tuning_support else "No",
                "Streaming": "Yes" if features.streaming_support else "No",
                "Vision": "Yes" if features.supports_vision else "No",
                "Audio": "Yes" if features.supports_audio else "No",
                "Reasoning": reasoning
            })
        
        # Convert to DataFrame and display
        feature_df = pd.DataFrame(feature_data)
        st.dataframe(
            feature_df,
            hide_index=True,
            use_container_width=True
        )
        
        # Resource Requirements Comparison
        has_resource_requirements = any(
            hasattr(agent, 'resource_requirements') and agent.resource_requirements
            for agent in selected_agents
        )
        
        if has_resource_requirements:
            st.subheader("Resource Requirements")
            
            resource_data = []
            for agent in selected_agents:
                if hasattr(agent, 'resource_requirements') and agent.resource_requirements:
                    reqs = agent.resource_requirements
                    resource_data.append({
                        "Agent": agent.name,
                        "Min CPU": reqs.min_cpu or "N/A",
                        "Recommended CPU": reqs.recommended_cpu or "N/A",
                        "Min RAM": reqs.min_ram or "N/A",
                        "Recommended RAM": reqs.recommended_ram or "N/A",
                        "GPU Required": "Yes" if reqs.gpu_required else "No",
                        "Recommended GPU": reqs.recommended_gpu or "N/A",
                        "Est. Cost/Hour": f"${reqs.estimated_cost_per_hour:.2f}" if reqs.estimated_cost_per_hour else "N/A"
                    })
                else:
                    resource_data.append({
                        "Agent": agent.name,
                        "Min CPU": "N/A",
                        "Recommended CPU": "N/A",
                        "Min RAM": "N/A",
                        "Recommended RAM": "N/A",
                        "GPU Required": "No",
                        "Recommended GPU": "N/A",
                        "Est. Cost/Hour": "N/A"
                    })
            
            # Convert to DataFrame and display
            resource_df = pd.DataFrame(resource_data)
            st.dataframe(
                resource_df,
                hide_index=True,
                use_container_width=True
            )
    
    with tab3:
        # LLM Support Comparison
        st.subheader("LLM Support")
        
        # Check if any agents have LLM support
        has_llm_support = any(agent.supported_llms for agent in selected_agents)
        
        if has_llm_support:
            # Create a set of all unique LLMs
            all_llms = set()
            for agent in selected_agents:
                for llm in agent.supported_llms:
                    # Use provider name if available, otherwise use provider_id or "Unknown"
                    provider_name = "Unknown"
                    if hasattr(llm, 'provider') and llm.provider:
                        provider_name = llm.provider.name
                    elif hasattr(llm, 'provider_id') and llm.provider_id:
                        provider = provider_dict.get(llm.provider_id)
                        if provider:
                            provider_name = provider.name
                    
                    all_llms.add(f"{llm.model_name} ({provider_name})")
            
            if all_llms:
                llm_data = []
                for agent in selected_agents:
                    agent_llms = {}
                    
                    # Get supported LLMs for this agent
                    for llm in agent.supported_llms:
                        provider_name = "Unknown"
                        if hasattr(llm, 'provider') and llm.provider:
                            provider_name = llm.provider.name
                        elif hasattr(llm, 'provider_id') and llm.provider_id:
                            provider = provider_dict.get(llm.provider_id)
                            if provider:
                                provider_name = provider.name
                        
                        llm_key = f"{llm.model_name} ({provider_name})"
                        agent_llms[llm_key] = {
                            "Rating": llm.performance_rating if hasattr(llm, 'performance_rating') and llm.performance_rating else None,
                            "Min Version": llm.min_version if hasattr(llm, 'min_version') and llm.min_version else None
                        }
                    
                    # Create a row for this agent
                    row = {"Agent": agent.name}
                    for llm in sorted(all_llms):
                        if llm in agent_llms:
                            # Use stars or rating number
                            rating = agent_llms[llm]["Rating"]
                            rating_str = f"★{rating}" if rating else "✓"
                            
                            # Add version if available
                            min_version = agent_llms[llm]["Min Version"]
                            version_str = f" (v{min_version})" if min_version else ""
                            
                            row[llm] = f"{rating_str}{version_str}"
                        else:
                            row[llm] = "✗"
                    
                    llm_data.append(row)
                
                # Convert to DataFrame and display
                llm_df = pd.DataFrame(llm_data)
                st.dataframe(
                    llm_df,
                    hide_index=True,
                    use_container_width=True
                )
                
                # LLM Details
                st.subheader("LLM Details")
                
                for agent in selected_agents:
                    if agent.supported_llms:
                        with st.expander(f"{agent.name} LLM Support"):
                            for llm in agent.supported_llms:
                                provider_name = "Unknown"
                                if hasattr(llm, 'provider') and llm.provider:
                                    provider_name = llm.provider.name
                                elif hasattr(llm, 'provider_id') and llm.provider_id:
                                    provider = provider_dict.get(llm.provider_id)
                                    if provider:
                                        provider_name = provider.name
                                
                                st.markdown(f"**{llm.model_name}** ({provider_name})")
                                
                                details = []
                                if hasattr(llm, 'min_version') and llm.min_version:
                                    details.append(f"Min Version: {llm.min_version}")
                                if hasattr(llm, 'performance_rating') and llm.performance_rating:
                                    details.append(f"Rating: {'★' * llm.performance_rating}")
                                
                                if details:
                                    st.markdown(" | ".join(details))
                                
                                if hasattr(llm, 'notes') and llm.notes:
                                    st.markdown(f"*{llm.notes}*")
                                
                                st.markdown("---")
            else:
                st.info("No LLM support information available for the selected agents.")
        else:
            st.info("None of the selected agents have defined LLM support information.")