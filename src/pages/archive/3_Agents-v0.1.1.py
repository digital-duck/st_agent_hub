import streamlit as st
import datetime
import os
import sys

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schema import (
    AgentMetadata, AgentFeatures, AgentDomain, 
    MemoryType, PlanningCapability, ToolUseCapability,
    LLMSupport, VectorStore, MemoryStore, CodeSnippet,
    ResourceRequirement
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
st.header("AI Agents")

# Tabs for listing and adding agents
tab1, tab2 = st.tabs(["List Agents", "Add/Edit Agent"])

with tab1:
    agents = db.get_all_agents()
    if not agents:
        st.info("No agents added yet. Use the 'Add/Edit Agent' tab to add some.")
    else:
        for agent in agents:
            with st.expander(f"{agent.name} (v{agent.version})"):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"**Description**: {agent.description}")
                    
                    # Get provider details
                    provider = db.get_provider(agent.provider_id)
                    provider_name = "Unknown"
                    provider_type = "Unknown"
                    if provider:
                        provider_name = provider.name
                        provider_type = provider.provider_type.value.capitalize()
                    
                    st.markdown(f"**Provider**: {provider_name} ({provider_type})")
                    
                    # Display domains
                    st.markdown("**Domains**:")
                    st.write(', '.join([domain.value for domain in agent.domains]))
                    
                    # Display features
                    st.markdown("**Features**:")
                    st.markdown(f"- Planning: {agent.features.planning.value}")
                    st.markdown(f"- Memory: {', '.join([m.value for m in agent.features.memory])}")
                    st.markdown(f"- Tool Use: {agent.features.tool_use.value}")
                    st.markdown(f"- Multi-agent Collaboration: {'Yes' if agent.features.multi_agent_collaboration else 'No'}")
                    st.markdown(f"- Human-in-the-loop: {'Yes' if agent.features.human_in_the_loop else 'No'}")
                    
                    # Display supported LLMs
                    if agent.supported_llms:
                        st.markdown("**Supported LLMs**:")
                        for llm in agent.supported_llms:
                            st.markdown(f"- {llm.model_name} ({llm.provider})")
                
                with col2:
                    st.markdown(f"**ID**: `{agent.id}`")
                    st.markdown(f"**Added**: {agent.created_at.strftime('%Y-%m-%d')}")
                    
                    # Display github/docs links
                    if agent.github_url:
                        st.markdown(f"**GitHub**: [{agent.github_url}]({agent.github_url})")
                    if agent.docs_url:
                        st.markdown(f"**Documentation**: [{agent.docs_url}]({agent.docs_url})")
                    if agent.demo_url:
                        st.markdown(f"**Demo**: [{agent.demo_url}]({agent.demo_url})")
                    
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
                
                # Display code snippets if available
                if agent.code_snippets:
                    st.markdown("**Code Snippets:**")
                    for snippet in agent.code_snippets:
                        with st.expander(f"{snippet.description} ({snippet.language})"):
                            st.code(snippet.code, language=snippet.language)
                            if snippet.import_requirements:
                                st.markdown(f"**Requirements**: {', '.join(snippet.import_requirements)}")

with tab2:
    st.header("Add/Edit Agent")
    
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
    
    # Get all providers for dropdown
    providers = db.get_all_providers()
    
    if not providers:
        st.warning("You need to add at least one provider before adding an agent. Go to the Providers section.")
        st.stop()
    
    # Agent form - Basic Information
    with st.form("agent_form"):
        st.subheader("Basic Information")
        
        name = st.text_input("Agent Name", value=editing_agent.name if editing_agent else "")
        description = st.text_area("Description", value=editing_agent.description if editing_agent else "")
        version = st.text_input("Version", value=editing_agent.version if editing_agent else "1.0.0")
        
        # Provider selection
        provider_options = {p.id: f"{p.name} ({p.provider_type.value})" for p in providers}
        provider_id = st.selectbox(
            "Provider", 
            options=list(provider_options.keys()),
            format_func=lambda x: provider_options[x],
            index=list(provider_options.keys()).index(editing_agent.provider_id) if editing_agent and editing_agent.provider_id in provider_options else 0
        )
        
        # URLs
        github_url = url_input("GitHub URL (optional)", value=editing_agent.github_url if editing_agent else None)
        docs_url = url_input("Documentation URL (optional)", value=editing_agent.docs_url if editing_agent else None)
        demo_url = url_input("Demo URL (optional)", value=editing_agent.demo_url if editing_agent else None)
        
        # Domains
        st.subheader("Domains")
        domains = []
        domain_cols = st.columns(3)
        for i, domain in enumerate(AgentDomain):
            col_idx = i % 3
            selected = False
            if editing_agent:
                selected = domain in editing_agent.domains
            if domain_cols[col_idx].checkbox(domain.value, value=selected, key=f"domain_{domain.value}"):
                domains.append(domain)
        
        # Tags
        tags_input = st.text_input(
            "Tags (comma-separated)", 
            value=",".join(editing_agent.tags) if editing_agent else ""
        )
        tags = [tag.strip() for tag in tags_input.split(",")] if tags_input else []
        
        # Features
        st.subheader("Features")
        col1, col2 = st.columns(2)
        
        with col1:
            planning = st.selectbox(
                "Planning Capability", 
                options=[p.value for p in PlanningCapability],
                index=[p.value for p in PlanningCapability].index(editing_agent.features.planning.value) if editing_agent else 0
            )
            
            tool_use = st.selectbox(
                "Tool Use Capability", 
                options=[t.value for t in ToolUseCapability],
                index=[t.value for t in ToolUseCapability].index(editing_agent.features.tool_use.value) if editing_agent else 0
            )
            
            # Memory types
            st.write("Memory Types:")
            memory_types = []
            for memory_type in MemoryType:
                selected = False
                if editing_agent:
                    selected = memory_type in editing_agent.features.memory
                if st.checkbox(memory_type.value, value=selected, key=f"memory_{memory_type.value}"):
                    memory_types.append(memory_type)
        
        with col2:
            multi_agent = st.checkbox(
                "Multi-agent Collaboration", 
                value=editing_agent.features.multi_agent_collaboration if editing_agent else False
            )
            
            human_in_loop = st.checkbox(
                "Human-in-the-loop", 
                value=editing_agent.features.human_in_the_loop if editing_agent else False
            )
            
            autonomous = st.checkbox(
                "Autonomous", 
                value=editing_agent.features.autonomous if editing_agent else False
            )
            
            fine_tuning = st.checkbox(
                "Fine-tuning Support", 
                value=editing_agent.features.fine_tuning_support if editing_agent else False
            )
            
            streaming = st.checkbox(
                "Streaming Support", 
                value=editing_agent.features.streaming_support if editing_agent else False
            )
            
            vision = st.checkbox(
                "Vision Support", 
                value=editing_agent.features.supports_vision if editing_agent else False
            )
            
            audio = st.checkbox(
                "Audio Support", 
                value=editing_agent.features.supports_audio if editing_agent else False
            )
        
        # Reasoning frameworks
        reasoning_input = st.text_input(
            "Reasoning Frameworks (comma-separated, e.g., ReAct, CoT, ToT)", 
            value=",".join(editing_agent.features.reasoning_frameworks) if editing_agent else ""
        )
        reasoning_frameworks = [r.strip() for r in reasoning_input.split(",")] if reasoning_input else []
        
        # Supported LLMs
        st.subheader("Supported LLMs")
        
        if 'llm_count' not in st.session_state:
            st.session_state.llm_count = 1
            if editing_agent and editing_agent.supported_llms:
                st.session_state.llm_count = len(editing_agent.supported_llms)
        
        if st.button("Add LLM"):
            st.session_state.llm_count += 1
        
        llms = []
        for i in range(st.session_state.llm_count):
            with st.container():
                st.markdown(f"**LLM #{i+1}**")
                
                llm_col1, llm_col2 = st.columns(2)
                
                default_model = ""
                default_provider = ""
                default_min_version = ""
                default_notes = ""
                default_rating = 3
                
                if editing_agent and i < len(editing_agent.supported_llms):
                    default_model = editing_agent.supported_llms[i].model_name
                    default_provider = editing_agent.supported_llms[i].provider
                    default_min_version = editing_agent.supported_llms[i].min_version or ""
                    default_notes = editing_agent.supported_llms[i].notes or ""
                    default_rating = editing_agent.supported_llms[i].performance_rating or 3
                
                with llm_col1:
                    model_name = st.text_input("Model Name", value=default_model, key=f"llm_model_{i}")
                    provider_name = st.text_input("Provider", value=default_provider, key=f"llm_provider_{i}")
                
                with llm_col2:
                    min_version = st.text_input("Min Version (optional)", value=default_min_version, key=f"llm_min_version_{i}")
                    performance = st.slider("Performance Rating", 1, 5, default_rating, key=f"llm_performance_{i}")
                
                notes = st.text_area("Notes (optional)", value=default_notes, key=f"llm_notes_{i}", height=50)
                
                if model_name and provider_name:
                    llms.append(LLMSupport(
                        model_name=model_name,
                        provider=provider_name,
                        min_version=min_version if min_version else None,
                        notes=notes if notes else None,
                        performance_rating=performance
                    ))
        
        # Code Snippets
        st.subheader("Code Snippets")
        
        if 'code_snippet_count' not in st.session_state:
            st.session_state.code_snippet_count = 1
            if editing_agent and editing_agent.code_snippets:
                st.session_state.code_snippet_count = len(editing_agent.code_snippets)
        
        if st.button("Add Code Snippet"):
            st.session_state.code_snippet_count += 1
        
        code_snippets = []
        for i in range(st.session_state.code_snippet_count):
            with st.container():
                st.markdown(f"**Code Snippet #{i+1}**")
                
                default_lang = "python"
                default_desc = ""
                default_code = ""
                default_reqs = ""
                
                if editing_agent and i < len(editing_agent.code_snippets):
                    default_lang = editing_agent.code_snippets[i].language
                    default_desc = editing_agent.code_snippets[i].description
                    default_code = editing_agent.code_snippets[i].code
                    default_reqs = ",".join(editing_agent.code_snippets[i].import_requirements) if editing_agent.code_snippets[i].import_requirements else ""
                
                cs_lang = st.text_input("Language", value=default_lang, key=f"cs_lang_{i}")
                cs_desc = st.text_input("Description", value=default_desc, key=f"cs_desc_{i}")
                cs_reqs = st.text_input("Import Requirements (comma-separated)", value=default_reqs, key=f"cs_reqs_{i}")
                cs_code = st.text_area("Code", value=default_code, key=f"cs_code_{i}", height=150)
                
                if cs_lang and cs_desc and cs_code:
                    reqs = [r.strip() for r in cs_reqs.split(",")] if cs_reqs else None
                    code_snippets.append(CodeSnippet(
                        language=cs_lang,
                        description=cs_desc,
                        code=cs_code,
                        import_requirements=reqs
                    ))
        
        # Form submission
        submitted = st.form_submit_button("Save Agent")
        if submitted:
            if not name or not description or not version or not provider_id:
                st.error("Name, description, version, and provider are required!")
            elif not domains:
                st.error("Please select at least one domain for the agent.")
            elif not memory_types:
                st.error("Please select at least one memory type.")
            else:
                try:
                    # Create agent features
                    features = AgentFeatures(
                        planning=PlanningCapability(planning),
                        memory=memory_types,
                        tool_use=ToolUseCapability(tool_use),
                        multi_agent_collaboration=multi_agent,
                        human_in_the_loop=human_in_loop,
                        autonomous=autonomous,
                        fine_tuning_support=fine_tuning,
                        streaming_support=streaming,
                        supports_vision=vision,
                        supports_audio=audio,
                        reasoning_frameworks=reasoning_frameworks
                    )
                    
                    # Create or update agent
                    if editing_agent:
                        agent = AgentMetadata(
                            id=editing_agent.id,
                            name=name,
                            description=description,
                            version=version,
                            provider_id=provider_id,
                            features=features,
                            supported_llms=llms,
                            code_snippets=code_snippets,
                            domains=domains,
                            tags=tags,
                            github_url=github_url,
                            docs_url=docs_url,
                            demo_url=demo_url,
                            created_at=editing_agent.created_at,
                            updated_at=datetime.datetime.now()
                        )
                        db.update_agent(agent)
                        st.success(f"Agent '{name}' updated successfully!")
                        # Clear the session state
                        st.session_state.pop("edit_agent", None)
                    else:
                        agent = AgentMetadata(
                            name=name,
                            description=description,
                            version=version,
                            provider_id=provider_id,
                            features=features,
                            supported_llms=llms,
                            code_snippets=code_snippets,
                            domains=domains,
                            tags=tags,
                            github_url=github_url,
                            docs_url=docs_url,
                            demo_url=demo_url
                        )
                        db.add_agent(agent)
                        st.success(f"Agent '{name}' added successfully!")
                    
                    # Clear form
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving agent: {str(e)}")