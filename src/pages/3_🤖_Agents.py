import streamlit as st
import datetime
import os
import sys
import uuid

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schema import (
    AgentMetadata, AgentFeatures, AgentDomain, 
    MemoryType, PlanningCapability, ToolUseCapability,
    LLMSupport, VectorStore, MemoryStore, CodeSnippet,
    ResourceRequirement, ProviderType
)
from database import JSONDatabase
from app import url_input, get_provider_options

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
st.title("🤖 AI Agents")
st.markdown("""
Manage AI agents from different providers. Add details about their capabilities, features, and implementation details.
""")

# Tab labels
tab_labels = ["Browse Agents", "Add New Agent", "Edit Agent"]

# Set active tab based on session state
active_tab_index = 0
if "active_tab" in st.session_state:
    active_tab_index = st.session_state["active_tab"]

# Create tabs with string labels
tabs = st.tabs(tab_labels)
tab1, tab2, tab3 = tabs

# Check for agent ID in session state (for editing)
editing_agent = None
agent_id = st.session_state.get("selected_agent_id")
if agent_id:
    editing_agent = db.get_agent(agent_id)
    # Switch to the Edit tab if we have a selected agent
    st.session_state["active_tab"] = 2
    # We can't directly select the tab, but we've set the state for the next rerun

# Clear active tab state if it's the edit tab but no provider is selected
if "active_tab" in st.session_state and st.session_state["active_tab"] == 2 and not editing_agent:
    del st.session_state["active_tab"]

# Function to display agent details
def display_agent_details(agent):
    """Display the details of an agent in a consistent format."""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"**Description**: {agent.description}")
        
        # Get provider details
        provider_name = "Unknown"
        provider_type = "Unknown"
        if agent.provider:
            provider_name = agent.provider.name
            provider_type = agent.provider.provider_type.value.capitalize()
        
        st.markdown(f"**Provider**: {provider_name} ({provider_type})")
        
        # Display domains
        st.markdown("**Domains**:")
        st.write(', '.join([domain.value for domain in agent.domains]))
        
        # Display features
        st.markdown("**Features**:")
        st.markdown(f"- **Planning**: {agent.features.planning.value}")
        st.markdown(f"- **Memory**: {', '.join([m.value for m in agent.features.memory])}")
        st.markdown(f"- **Tool Use**: {agent.features.tool_use.value}")
        st.markdown(f"- **Multi-agent Collaboration**: {'Yes' if agent.features.multi_agent_collaboration else 'No'}")
        st.markdown(f"- **Human-in-the-loop**: {'Yes' if agent.features.human_in_the_loop else 'No'}")
        
        # Display supported LLMs
        if agent.supported_llms:
            st.markdown("**Supported LLMs**:")
            for llm in agent.supported_llms:
                provider_info = f" ({llm.provider.name})" if llm.provider else ""
                st.markdown(f"- {llm.model_name}{provider_info} - Rating: {llm.performance_rating}/5")
    
    with col2:
        st.markdown(f"**ID**: `{agent.id}`")
        st.markdown(f"**Version**: {agent.version}")
        st.markdown(f"**Added**: {agent.created_at.strftime('%Y-%m-%d')}")
        st.markdown(f"**Updated**: {agent.updated_at.strftime('%Y-%m-%d')}")
        
        # Display links
        if agent.github_url:
            st.markdown(f"[GitHub Repository]({agent.github_url})")
        if agent.docs_url:
            st.markdown(f"[Documentation]({agent.docs_url})")
        if agent.demo_url:
            st.markdown(f"[Live Demo]({agent.demo_url})")
        
        # Tags
        if agent.tags:
            st.markdown("**Tags**:")
            st.markdown(", ".join(agent.tags))

# Tab 1: Browse Agents
with tab1:
    # Search and filter options
    st.subheader("Search and Filter")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_query = st.text_input("Search by name or description", placeholder="Search...")
    
    with col2:
        provider_filter_options = get_provider_options(db, include_none=True)
        provider_filter_options["all"] = "All Providers"
        provider_filter = st.selectbox(
            "Filter by Provider",
            options=["all"] + list(provider_filter_options.keys())[:-1],  # Add "all" at beginning, exclude "none"
            format_func=lambda x: "All Providers" if x == "all" else provider_filter_options[x]
        )
    
    with col3:
        domain_options = {d.value: d.value.capitalize() for d in AgentDomain}
        domain_options["all"] = "All Domains"
        domain_filter = st.selectbox(
            "Filter by Domain",
            options=["all"] + list(domain_options.keys())[:-1],  # Add "all" at beginning, exclude "none"
            format_func=lambda x: "All Domains" if x == "all" else domain_options[x].capitalize()
        )
    
    # Get and filter agents
    agents = db.get_all_agents()
    
    # Apply provider filter
    if provider_filter != "all":
        agents = [a for a in agents if a.provider_id == provider_filter]
    
    # Apply domain filter
    if domain_filter != "all":
        domain_enum = AgentDomain(domain_filter)
        agents = [a for a in agents if domain_enum in a.domains]
    
    # Apply search query
    if search_query:
        search_query = search_query.lower()
        agents = [a for a in agents if search_query in a.name.lower() or search_query in a.description.lower()]
    
    # Display results
    if not agents:
        st.info("No agents found matching your criteria. Try adjusting your filters or add a new agent.")
    else:
        st.subheader(f"Results ({len(agents)} agents)")
        
        # Option to view as cards or table
        view_type = st.radio("View as", ["Cards", "Table"], horizontal=True)
        
        if view_type == "Cards":
            # Create rows of 3 cards each
            for i in range(0, len(agents), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(agents):
                        agent = agents[i + j]
                        with cols[j]:
                            with st.container(border=True):
                                st.subheader(agent.name)
                                st.caption(f"v{agent.version}")
                                
                                # Get provider name
                                provider_name = "Unknown"
                                if agent.provider:
                                    provider_name = agent.provider.name
                                
                                st.markdown(f"**Provider**: {provider_name}")
                                
                                # Truncate description
                                desc = agent.description
                                if len(desc) > 100:
                                    desc = desc[:100] + "..."
                                st.markdown(desc)
                                
                                # Key features
                                st.markdown(f"**Planning**: {agent.features.planning.value}")
                                st.markdown(f"**Tool Use**: {agent.features.tool_use.value}")
                                
                                # Action buttons
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button("View Details", key=f"view_{agent.id}"):
                                        with st.expander(f"{agent.name} Details", expanded=True):
                                            display_agent_details(agent)
                                with col2:
                                    if st.button("Edit", key=f"edit_{agent.id}"):
                                        st.session_state["selected_agent_id"] = agent.id
                                        st.session_state["active_tab"] = 2
                                        st.rerun()
        else:  # Table view
            # Create a simplified table view
            data = []
            for agent in agents:
                provider_name = agent.provider.name if agent.provider else "Unknown"
                domains = ", ".join([d.value for d in agent.domains])
                data.append({
                    "Name": agent.name,
                    "Version": agent.version,
                    "Provider": provider_name,
                    "Planning": agent.features.planning.value,
                    "Tool Use": agent.features.tool_use.value,
                    "Domains": domains,
                    "ID": agent.id
                })
            
            # Convert to DataFrame for display
            import pandas as pd
            df = pd.DataFrame(data)
            
            # Add action buttons
            st.dataframe(
                df.drop(columns=["ID"]),
                column_config={
                    "Name": st.column_config.TextColumn("Name"),
                    "Version": st.column_config.TextColumn("Version"),
                    "Provider": st.column_config.TextColumn("Provider"),
                    "Planning": st.column_config.TextColumn("Planning"),
                    "Tool Use": st.column_config.TextColumn("Tool Use"),
                    "Domains": st.column_config.TextColumn("Domains")
                },
                hide_index=True
            )
            
            # Agent selection for actions
            selected_agent_id = st.selectbox(
                "Select an agent for actions", 
                options=[a.id for a in agents],
                format_func=lambda x: next((a.name for a in agents if a.id == x), "")
            )
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("View Details", key="view_selected"):
                    selected_agent = next((a for a in agents if a.id == selected_agent_id), None)
                    if selected_agent:
                        with st.expander(f"{selected_agent.name} Details", expanded=True):
                            display_agent_details(selected_agent)
            with col2:
                if st.button("Edit Agent", key="edit_selected"):
                    st.session_state["selected_agent_id"] = selected_agent_id
                    st.session_state["active_tab"] = 2
                    st.rerun()
            with col3:
                if st.button("Delete Agent", key="delete_selected"):
                    if st.warning(f"Are you sure you want to delete this agent? This action cannot be undone."):
                        if db.delete_agent(selected_agent_id):
                            st.success("Agent deleted successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to delete agent.")

# Function to display agent form fields
def agent_form_fields(editing_agent=None):
    """Display form fields for adding/editing an agent."""
    # Get all providers for dropdown
    providers = db.get_all_providers()
    
    if not providers:
        st.warning("You need to add at least one provider before adding an agent. Go to the Providers section.")
        st.stop()
    
    st.subheader("Basic Information")
    
    name = st.text_input("Agent Name", value=editing_agent.name if editing_agent else "")
    description = st.text_area("Description", value=editing_agent.description if editing_agent else "")
    version = st.text_input("Version", value=editing_agent.version if editing_agent else "1.0.0")
    
    # Provider selection
    provider_options = get_provider_options(db, include_none=False)
    
    provider_id = st.selectbox(
        "Provider", 
        options=list(provider_options.keys()),
        format_func=lambda x: provider_options[x],
        index=list(provider_options.keys()).index(editing_agent.provider_id) if editing_agent and editing_agent.provider_id in provider_options else 0
    )
    
    # URLs
    col1, col2, col3 = st.columns(3)
    with col1:
        github_url = url_input("GitHub URL (optional)", value=editing_agent.github_url if editing_agent else None)
    with col2:
        docs_url = url_input("Documentation URL (optional)", value=editing_agent.docs_url if editing_agent else None)
    with col3:
        demo_url = url_input("Demo URL (optional)", value=editing_agent.demo_url if editing_agent else None)
    
    # Domains
    st.subheader("Domains")
    st.markdown("Select all domains that apply to this agent:")
    
    domains = []
    domain_cols = st.columns(4)
    for i, domain in enumerate(AgentDomain):
        key_id = uuid.uuid4()
        col_idx = i % 4
        selected = False
        if editing_agent:
            selected = domain in editing_agent.domains
        if domain_cols[col_idx].checkbox(domain.value, value=selected, key=f"domain_{key_id}"):
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
            key_id = uuid.uuid4()
            selected = False
            if editing_agent:
                selected = memory_type in editing_agent.features.memory
            key_val = f"memory_{key_id}" # f"memory_{memory_type.value}"
            if st.checkbox(memory_type.value, value=selected, key=key_val):
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
        
        supports_vision = st.checkbox(
            "Vision Support", 
            value=editing_agent.features.supports_vision if editing_agent else False
        )
        
        supports_audio = st.checkbox(
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
    
    # LLM counter
    if 'llm_count' not in st.session_state:
        st.session_state.llm_count = 1
        if editing_agent and editing_agent.supported_llms:
            st.session_state.llm_count = len(editing_agent.supported_llms)
    
    llms = []
    for i in range(st.session_state.llm_count):
        key_id = uuid.uuid4()
        with st.container(border=True):
            st.markdown(f"**LLM #{i+1}**")
            
            llm_col1, llm_col2 = st.columns(2)
            
            default_model = ""
            default_provider_id = None
            default_min_version = ""
            default_notes = ""
            default_rating = 3
            
            if editing_agent and i < len(editing_agent.supported_llms):
                default_model = editing_agent.supported_llms[i].model_name
                if editing_agent.supported_llms[i].provider_id:
                    default_provider_id = editing_agent.supported_llms[i].provider_id
                default_min_version = editing_agent.supported_llms[i].min_version or ""
                default_notes = editing_agent.supported_llms[i].notes or ""
                default_rating = editing_agent.supported_llms[i].performance_rating or 3
            
            with llm_col1:
                key_val = f"llm_model_{key_id}"  # f"llm_model_{i}"
                model_name = st.text_input("Model Name", value=default_model, key=key_val)
                
                # Provider dropdown for LLM
                llm_provider_options = get_provider_options(db, include_none=True)
                llm_provider_id = st.selectbox(
                    "Provider", 
                    options=list(llm_provider_options.keys()),
                    format_func=lambda x: llm_provider_options[x],
                    index=list(llm_provider_options.keys()).index(default_provider_id) if default_provider_id in llm_provider_options else 0,
                    key=f"llm_provider_{key_id}"
                )
                
                if llm_provider_id == "none":
                    llm_provider_id = None
            
            with llm_col2:
                min_version = st.text_input("Min Version (optional)", value=default_min_version, key=f"llm_min_version_{key_id}")
                performance = st.slider("Performance Rating", 1, 5, default_rating, key=f"llm_performance_{key_id}")
            
            notes = st.text_area("Notes (optional)", value=default_notes, key=f"llm_notes_{key_id}", height=70)
            
            if model_name:
                llms.append(LLMSupport(
                    model_name=model_name,
                    provider_id=llm_provider_id,
                    min_version=min_version if min_version else None,
                    notes=notes if notes else None,
                    performance_rating=performance
                ))
    
    # Code Snippets
    st.subheader("Code Snippets")
    
    # Code snippet counter
    if 'code_snippet_count' not in st.session_state:
        st.session_state.code_snippet_count = 1
        if editing_agent and editing_agent.code_snippets:
            st.session_state.code_snippet_count = len(editing_agent.code_snippets)
    
    code_snippets = []
    for i in range(st.session_state.code_snippet_count):
        key_id = uuid.uuid4()
        with st.container(border=True):
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
            
            cs_col1, cs_col2 = st.columns(2)
            
            with cs_col1:
                cs_lang = st.text_input("Language", value=default_lang, key=f"cs_lang_{key_id}")
                cs_desc = st.text_input("Description", value=default_desc, key=f"cs_desc_{key_id}")
            
            with cs_col2:
                cs_reqs = st.text_input("Import Requirements (comma-separated)", value=default_reqs, key=f"cs_reqs_{key_id}")
            
            cs_code = st.text_area("Code", value=default_code, key=f"cs_code_{key_id}", height=150)
            
            if cs_lang and cs_desc and cs_code:
                reqs = [r.strip() for r in cs_reqs.split(",")] if cs_reqs else None
                code_snippets.append(CodeSnippet(
                    language=cs_lang,
                    description=cs_desc,
                    code=cs_code,
                    import_requirements=reqs
                ))
    
    # Resource Requirements
    st.subheader("Resource Requirements (Optional)")
    
    resource_col1, resource_col2 = st.columns(2)
    
    default_min_cpu = ""
    default_recommended_cpu = ""
    default_min_ram = ""
    default_recommended_ram = ""
    default_gpu_required = False
    default_recommended_gpu = ""
    default_cost_per_hour = None
    default_resource_notes = ""
    
    if editing_agent and editing_agent.resource_requirements:
        default_min_cpu = editing_agent.resource_requirements.min_cpu or ""
        default_recommended_cpu = editing_agent.resource_requirements.recommended_cpu or ""
        default_min_ram = editing_agent.resource_requirements.min_ram or ""
        default_recommended_ram = editing_agent.resource_requirements.recommended_ram or ""
        default_gpu_required = editing_agent.resource_requirements.gpu_required
        default_recommended_gpu = editing_agent.resource_requirements.recommended_gpu or ""
        default_cost_per_hour = editing_agent.resource_requirements.estimated_cost_per_hour
        default_resource_notes = editing_agent.resource_requirements.notes or ""
    
    with resource_col1:
        min_cpu = st.text_input("Minimum CPU", value=default_min_cpu)
        min_ram = st.text_input("Minimum RAM", value=default_min_ram)
        gpu_required = st.checkbox("GPU Required", value=default_gpu_required)
        
        if default_cost_per_hour is not None:
            cost_per_hour = st.number_input("Estimated Cost per Hour ($)", value=default_cost_per_hour, min_value=0.0, format="%.2f")
        else:
            cost_per_hour = st.number_input("Estimated Cost per Hour ($)", value=0.0, min_value=0.0, format="%.2f")
    
    with resource_col2:
        recommended_cpu = st.text_input("Recommended CPU", value=default_recommended_cpu)
        recommended_ram = st.text_input("Recommended RAM", value=default_recommended_ram)
        recommended_gpu = st.text_input("Recommended GPU", value=default_recommended_gpu)
        resource_notes = st.text_area("Resource Notes", value=default_resource_notes, height=100)
    
    # Create resource requirements object
    resource_requirements = ResourceRequirement(
        min_cpu=min_cpu if min_cpu else None,
        recommended_cpu=recommended_cpu if recommended_cpu else None,
        min_ram=min_ram if min_ram else None,
        recommended_ram=recommended_ram if recommended_ram else None,
        gpu_required=gpu_required,
        recommended_gpu=recommended_gpu if recommended_gpu else None,
        estimated_cost_per_hour=cost_per_hour if cost_per_hour > 0 else None,
        notes=resource_notes if resource_notes else None
    )
    
    # Return all form values
    return {
        "name": name,
        "description": description,
        "version": version,
        "provider_id": provider_id,
        "domains": domains,
        "tags": tags,
        "github_url": github_url,
        "docs_url": docs_url,
        "demo_url": demo_url,
        "planning": planning,
        "memory_types": memory_types,
        "tool_use": tool_use,
        "multi_agent": multi_agent,
        "human_in_loop": human_in_loop,
        "autonomous": autonomous,
        "fine_tuning": fine_tuning,
        "streaming": streaming,
        "supports_vision": supports_vision,
        "supports_audio": supports_audio,
        "reasoning_frameworks": reasoning_frameworks,
        "llms": llms,
        "code_snippets": code_snippets,
        "resource_requirements": resource_requirements
    }

# Function to save agent data
def save_agent_data(form_data, editing_agent=None):
    """Save the agent data from form submission."""
    try:
        # Create agent features
        features = AgentFeatures(
            planning=PlanningCapability(form_data["planning"]),
            memory=form_data["memory_types"],
            tool_use=ToolUseCapability(form_data["tool_use"]),
            multi_agent_collaboration=form_data["multi_agent"],
            human_in_the_loop=form_data["human_in_loop"],
            autonomous=form_data["autonomous"],
            fine_tuning_support=form_data["fine_tuning"],
            streaming_support=form_data["streaming"],
            supports_vision=form_data["supports_vision"],
            supports_audio=form_data["supports_audio"],
            reasoning_frameworks=form_data["reasoning_frameworks"]
        )
        
        # Create or update agent
        if editing_agent:
            agent = AgentMetadata(
                id=editing_agent.id,
                name=form_data["name"],
                description=form_data["description"],
                version=form_data["version"],
                provider_id=form_data["provider_id"],
                features=features,
                supported_llms=form_data["llms"],
                code_snippets=form_data["code_snippets"],
                domains=form_data["domains"],
                tags=form_data["tags"],
                github_url=form_data["github_url"],
                docs_url=form_data["docs_url"],
                demo_url=form_data["demo_url"],
                resource_requirements=form_data["resource_requirements"],
                created_at=editing_agent.created_at,
                updated_at=datetime.datetime.now()
            )
            db.update_agent(agent)
            return True, f"Agent '{form_data['name']}' updated successfully!"
        else:
            agent = AgentMetadata(
                name=form_data["name"],
                description=form_data["description"],
                version=form_data["version"],
                provider_id=form_data["provider_id"],
                features=features,
                supported_llms=form_data["llms"],
                code_snippets=form_data["code_snippets"],
                domains=form_data["domains"],
                tags=form_data["tags"],
                github_url=form_data["github_url"],
                docs_url=form_data["docs_url"],
                demo_url=form_data["demo_url"],
                resource_requirements=form_data["resource_requirements"]
            )
            db.add_agent(agent)
            return True, f"Agent '{form_data['name']}' added successfully!"
    except Exception as e:
        return False, f"Error saving agent: {str(e)}"

# LLM and Code Snippet management buttons (OUTSIDE the form)
with tab2, tab3:
    # Only show these controls in the relevant tabs
    if (tab2 and st.session_state.get("active_tab") == 1) or (tab3 and st.session_state.get("active_tab") == 2 and editing_agent):
        # Create container for the management buttons
        with st.container():
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                if st.button("+ Add LLM"):
                    st.session_state.llm_count = st.session_state.get('llm_count', 1) + 1
                    st.rerun()
            with col2:
                if st.button("+ Add Code Snippet"):
                    st.session_state.code_snippet_count = st.session_state.get('code_snippet_count', 1) + 1
                    st.rerun()

# Tab 2: Add New Agent
with tab2:
    st.header("Add New Agent")
    
    with st.form("add_agent_form"):
        form_data = agent_form_fields()
        
        # Form submission
        submitted = st.form_submit_button("Add Agent")
        if submitted:
            if not form_data["name"] or not form_data["description"] or not form_data["version"] or not form_data["provider_id"]:
                st.error("Name, description, version, and provider are required fields!")
            elif not form_data["domains"]:
                st.error("Please select at least one domain for the agent.")
            elif not form_data["memory_types"]:
                st.error("Please select at least one memory type.")
            else:
                success, message = save_agent_data(form_data)
                if success:
                    st.success(message)
                    # Clear form by rerunning
                    st.session_state.llm_count = 1
                    st.session_state.code_snippet_count = 1
                    st.rerun()
                else:
                    st.error(message)

# Tab 3: Edit Agent
with tab3:
    if editing_agent:
        st.header(f"Edit Agent: {editing_agent.name}")
        
        # Cancel editing button
        if st.button("Cancel Editing"):
            st.session_state.pop("selected_agent_id", None)
            st.rerun()
        
        with st.form("edit_agent_form"):
            form_data = agent_form_fields(editing_agent)
            
            # Form submission
            submitted = st.form_submit_button("Update Agent")
            if submitted:
                if not form_data["name"] or not form_data["description"] or not form_data["version"] or not form_data["provider_id"]:
                    st.error("Name, description, version, and provider are required fields!")
                elif not form_data["domains"]:
                    st.error("Please select at least one domain for the agent.")
                elif not form_data["memory_types"]:
                    st.error("Please select at least one memory type.")
                else:
                    success, message = save_agent_data(form_data, editing_agent)
                    if success:
                        st.success(message)
                        # Clear session state and redirect to list view
                        st.session_state.pop("selected_agent_id", None)
                        st.session_state["active_tab"] = 0
                        st.rerun()
                    else:
                        st.error(message)
    else:  # No editing agent selected
        st.info("Select an agent from the 'Browse Agents' tab to edit.")
        
        # Option to go back to list view
        if st.button("Back to Agent List"):
            st.session_state["active_tab"] = 0
            st.rerun()