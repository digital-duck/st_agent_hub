import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional
import datetime

# Import our database and schema
from schema import (
    AgentMetadata, AgentFeatures, 
    LLMSupport, VectorStore, MemoryStore, CodeSnippet,
    PlanningCapability, ToolUseCapability, AgentDomain, MemoryType
)
from database import JSONDatabase
from app import url_input

# Set page configuration
st.set_page_config(
    page_title="AI Agent Hub - Agents",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
db = JSONDatabase()

# Page title
st.title("AI Agents")

# Tabs for listing and adding agents
tab1, tab2 = st.tabs(["List Agents", "Add/Edit Agent"])

with tab1:
    agents = db.get_all_agents()
    if not agents:
        st.info("No agents added yet. Use the 'Add/Edit Agent' tab to add some.")
    else:
        for agent in agents:
            with st.expander(f"{agent.name} (v{agent.version})"):
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
                    
                    # Display code snippets without nested expanders
                    if agent.code_snippets:
                        st.subheader("Code Snippets")
                        for i, snippet in enumerate(agent.code_snippets):
                            # Use a container with a border instead of an expander
                            with st.container(border=True):
                                st.caption(f"{snippet.description} ({snippet.language})")
                                st.code(snippet.code, language=snippet.language.lower())
                                if snippet.import_requirements:
                                    st.markdown(f"**Required imports**: {', '.join(snippet.import_requirements)}")
                
                with col2:
                    st.markdown(f"**ID**: `{agent.id}`")
                    st.markdown(f"**Version**: {agent.version}")
                    
                    if hasattr(agent, 'github_url') and agent.github_url:
                        st.markdown(f"**GitHub**: [{agent.github_url}]({agent.github_url})")
                    if hasattr(agent, 'docs_url') and agent.docs_url:
                        st.markdown(f"**Documentation**: [{agent.docs_url}]({agent.docs_url})")
                    
                    st.markdown(f"**Added**: {agent.created_at.strftime('%Y-%m-%d')}")
                    
                    # Edit and delete buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Edit", key=f"edit_{agent.id}"):
                            st.session_state["edit_agent"] = agent.id
                            st.rerun()
                    with col2:
                        if st.button("Delete", key=f"delete_{agent.id}"):
                            if db.delete_agent(agent.id):
                                st.success("Agent deleted!")
                                st.rerun()
                            else:
                                st.error("Failed to delete agent.")

with tab2:
    st.header("Add/Edit Agent")
    st.warning("This is a simplified form. In a real application, you would have more detailed inputs for agent features, LLMs, etc.")
    
    # Get providers for selection
    providers = db.get_all_providers()
    provider_options = {provider.id: provider.name for provider in providers}
    
    if not providers:
        st.error("Please add a provider first before adding an agent!")
        st.stop()
    
    # Check if we're editing an existing agent
    editing_agent = None
    agent_id = st.session_state.get("edit_agent")
    if agent_id:
        editing_agent = db.get_agent(agent_id)
        st.info(f"Editing agent: {editing_agent.name}")
        # Clear the session state for future runs
        if st.button("Cancel Editing"):
            st.session_state.pop("edit_agent", None)
            st.rerun()
    
    # Agent form
    with st.form("agent_form"):
        name = st.text_input("Agent Name", value=editing_agent.name if editing_agent else "")
        description = st.text_area("Description", value=editing_agent.description if editing_agent else "")
        version = st.text_input("Version", value=editing_agent.version if editing_agent else "0.1.0")
        
        provider_id = st.selectbox(
            "Provider", 
            options=list(provider_options.keys()),
            format_func=lambda x: provider_options.get(x, "Unknown"),
            index=list(provider_options.keys()).index(editing_agent.provider_id) if editing_agent else 0
        )
        
        # Simple inputs for more complex objects
        st.subheader("Features")
        
        planning_options = {p.name: p for p in PlanningCapability}
        planning = st.selectbox(
            "Planning Capability",
            options=list(planning_options.keys()),
            index=list(planning_options.keys()).index(editing_agent.features.planning.name) if editing_agent and editing_agent.features else 0
        )
        
        tool_use_options = {t.name: t for t in ToolUseCapability}
        tool_use = st.selectbox(
            "Tool Use Capability",
            options=list(tool_use_options.keys()),
            index=list(tool_use_options.keys()).index(editing_agent.features.tool_use.name) if editing_agent and editing_agent.features else 0
        )
        
        memory_options = {m.name: m for m in MemoryType}
        memory_types = st.multiselect(
            "Memory Types",
            options=list(memory_options.keys()),
            default=[m.name for m in editing_agent.features.memory] if editing_agent and editing_agent.features and editing_agent.features.memory else []
        )
        
        multi_agent = st.checkbox("Multi-Agent Collaboration", 
                                value=editing_agent.features.multi_agent_collaboration if editing_agent and editing_agent.features else False)
        human_in_loop = st.checkbox("Human-in-the-Loop", 
                                  value=editing_agent.features.human_in_the_loop if editing_agent and editing_agent.features else False)
        autonomous = st.checkbox("Autonomous", 
                               value=editing_agent.features.autonomous if editing_agent and editing_agent.features else False)
        
        reasoning_frameworks = st.text_input(
            "Reasoning Frameworks (comma-separated)",
            value=", ".join(editing_agent.features.reasoning_frameworks) if editing_agent and editing_agent.features and editing_agent.features.reasoning_frameworks else ""
        )
        
        # Domains
        domain_options = {d.name: d for d in AgentDomain}
        domains = st.multiselect(
            "Domains",
            options=list(domain_options.keys()),
            default=[d.name for d in editing_agent.domains] if editing_agent and editing_agent.domains else []
        )
        
        tags = st.text_input(
            "Tags (comma-separated)",
            value=", ".join(editing_agent.tags) if editing_agent and editing_agent.tags else ""
        )
        
        github_url = url_input("GitHub URL (optional)", 
                             value=editing_agent.github_url if editing_agent and hasattr(editing_agent, 'github_url') else None)
        docs_url = url_input("Documentation URL (optional)", 
                           value=editing_agent.docs_url if editing_agent and hasattr(editing_agent, 'docs_url') else None)
        
        # Add a simplified code snippet input
        st.subheader("Sample Code Snippet")
        snippet_desc = st.text_input("Snippet Description", 
                                   value=editing_agent.code_snippets[0].description if editing_agent and editing_agent.code_snippets and len(editing_agent.code_snippets) > 0 else "")
        snippet_lang = st.text_input("Language", 
                                   value=editing_agent.code_snippets[0].language if editing_agent and editing_agent.code_snippets and len(editing_agent.code_snippets) > 0 else "python")
        snippet_code = st.text_area("Code", height=200,
                                  value=editing_agent.code_snippets[0].code if editing_agent and editing_agent.code_snippets and len(editing_agent.code_snippets) > 0 else "")
        snippet_imports = st.text_input("Required imports (comma-separated)",
                                      value=", ".join(editing_agent.code_snippets[0].import_requirements) if editing_agent and editing_agent.code_snippets and len(editing_agent.code_snippets) > 0 and editing_agent.code_snippets[0].import_requirements else "")
        
        submitted = st.form_submit_button("Save Agent")
        if submitted:
            if not name or not description or not version or not provider_id:
                st.error("Name, description, version, and provider are required!")
            else:
                try:
                    # Process inputs
                    parsed_reasoning = [framework.strip() for framework in reasoning_frameworks.split(",")] if reasoning_frameworks else []
                    parsed_tags = [tag.strip() for tag in tags.split(",")] if tags else []
                    parsed_snippet_imports = [imp.strip() for imp in snippet_imports.split(",")] if snippet_imports else []
                    
                    # Create features object
                    features = AgentFeatures(
                        planning=planning_options[planning],
                        tool_use=tool_use_options[tool_use],
                        memory=[memory_options[m] for m in memory_types] if memory_types else [],
                        multi_agent_collaboration=multi_agent,
                        human_in_the_loop=human_in_loop,
                        autonomous=autonomous,
                        reasoning_frameworks=parsed_reasoning
                    )
                    
                    # Create code snippet if provided
                    code_snippets = []
                    if snippet_desc and snippet_lang and snippet_code:
                        code_snippets.append(CodeSnippet(
                            language=snippet_lang,
                            description=snippet_desc,
                            code=snippet_code,
                            import_requirements=parsed_snippet_imports
                        ))
                    
                    # Prepare agent data dictionary
                    agent_data = {
                        "name": name,
                        "description": description,
                        "version": version,
                        "provider_id": provider_id,
                        "features": features,
                        "domains": [domain_options[d] for d in domains] if domains else [],
                        "code_snippets": code_snippets,
                        "tags": parsed_tags,
                        "supported_llms": [],
                        "vector_stores": [],
                        "memory_stores": []
                    }
                    
                    # Add optional URL fields if provided
                    if github_url:
                        agent_data["github_url"] = github_url
                    if docs_url:
                        agent_data["docs_url"] = docs_url
                    
                    # Create or update agent
                    if editing_agent:
                        # Add ID and timestamps for update
                        agent_data["id"] = editing_agent.id
                        agent_data["created_at"] = editing_agent.created_at
                        agent_data["updated_at"] = datetime.datetime.now()
                        
                        # Preserve existing collections
                        agent_data["supported_llms"] = editing_agent.supported_llms
                        agent_data["vector_stores"] = editing_agent.vector_stores
                        agent_data["memory_stores"] = editing_agent.memory_stores
                        
                        # Create agent object
                        agent = AgentMetadata(**agent_data)
                        db.update_agent(agent)
                        st.success(f"Agent '{name}' updated successfully!")
                        # Clear the session state
                        st.session_state.pop("edit_agent", None)
                    else:
                        # Create agent object
                        agent = AgentMetadata(**agent_data)
                        db.add_agent(agent)
                        st.success(f"Agent '{name}' added successfully!")
                    
                    # Clear form
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving agent: {str(e)}")