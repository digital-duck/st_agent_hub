import streamlit as st
import datetime
import os
import sys

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schema import Provider, ProviderType
from database import JSONDatabase
from app import url_input

# Set page configuration
st.set_page_config(
    page_title="AI Agent Hub - Providers",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
db = JSONDatabase()

# Page title
st.title("🏢 AI Agent Providers & Frameworks")
st.markdown("""
Manage providers and frameworks that create AI agents. Add details like website links, 
documentation, and contact information.
""")

# Tab labels
tab_labels = ["Browse Providers", "Add Provider", "Edit Provider"]

# Set active tab based on session state
active_tab_index = 0
if "active_tab" in st.session_state:
    active_tab_index = st.session_state["active_tab"]

# Create tabs with string labels
tabs = st.tabs(tab_labels)
tab1, tab2, tab3 = tabs

# Check for provider ID in session state (for editing)
editing_provider = None
provider_id = st.session_state.get("selected_provider_id")
if provider_id:
    editing_provider = db.get_provider(provider_id)
    # Switch to the Edit tab if we have a selected provider
    st.session_state["active_tab"] = 2
    # We can't directly select the tab, but we've set the state for the next rerun

# Clear active tab state if it's the edit tab but no provider is selected
if "active_tab" in st.session_state and st.session_state["active_tab"] == 2 and not editing_provider:
    del st.session_state["active_tab"]

# Tab 1: Browse Providers
with tab1:
    # Filter providers by type
    provider_type_filter = st.radio(
        "Filter by type:", 
        options=["All", "Companies", "Frameworks", "Open Source", "Research", "Other"],
        horizontal=True
    )
    
    # Get filtered providers based on selection
    if provider_type_filter == "All":
        providers = db.get_all_providers()
    elif provider_type_filter == "Companies":
        providers = db.get_providers_by_type(ProviderType.COMPANY)
    elif provider_type_filter == "Frameworks":
        providers = db.get_providers_by_type(ProviderType.FRAMEWORK)
    elif provider_type_filter == "Open Source":
        providers = db.get_providers_by_type(ProviderType.OPEN_SOURCE)
    elif provider_type_filter == "Research":
        providers = db.get_providers_by_type(ProviderType.RESEARCH)
    else:
        providers = db.get_providers_by_type(ProviderType.OTHER)
    
    # Display providers based on selection
    if not providers:
        st.info("No providers found. Use the 'Add Provider' tab to add some.")
    else:
        # Count by type
        by_type = {}
        for p in providers:
            type_name = p.provider_type.value
            by_type[type_name] = by_type.get(type_name, 0) + 1
        
        # Display count by type
        st.caption(f"Displaying {len(providers)} providers: " + ", ".join([f"{count} {ptype}" for ptype, count in by_type.items()]))
        
        # Choose display mode
        display_mode = st.radio("View as", ["Cards", "Detailed List"], horizontal=True)
        
        if display_mode == "Cards":
            # Display as cards in a grid (3 per row)
            cols = st.columns(3)
            for i, provider in enumerate(providers):
                with cols[i % 3]:
                    with st.container(border=True):
                        st.subheader(provider.name)
                        st.caption(provider.provider_type.value.capitalize())
                        
                        # Truncate description if too long
                        desc = provider.description
                        if len(desc) > 150:
                            desc = desc[:150] + "..."
                        st.write(desc)
                        
                        # Links
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"[Website]({provider.url})")
                        with col2:
                            if provider.github_url:
                                st.markdown(f"[GitHub]({provider.github_url})")
                        
                        # Action buttons
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("View", key=f"view_{provider.id}"):
                                with st.expander(f"{provider.name} Details", expanded=True):
                                    st.markdown(f"**Type**: {provider.provider_type.value.capitalize()}")
                                    st.markdown(f"**Description**: {provider.description}")
                                    st.markdown(f"**Website**: [{provider.url}]({provider.url})")
                                    
                                    if provider.github_url:
                                        st.markdown(f"**GitHub**: [{provider.github_url}]({provider.github_url})")
                                    if provider.docs_url:
                                        st.markdown(f"**Documentation**: [{provider.docs_url}]({provider.docs_url})")
                                    if provider.logo_url:
                                        st.markdown(f"**Logo URL**: [{provider.logo_url}]({provider.logo_url})")
                                    
                                    if provider.provider_type == ProviderType.FRAMEWORK and provider.version:
                                        st.markdown(f"**Version**: {provider.version}")
                                    
                                    if provider.support_email:
                                        st.markdown(f"**Support Email**: {provider.support_email}")
                                    if provider.support_url:
                                        st.markdown(f"**Support URL**: [{provider.support_url}]({provider.support_url})")
                                    
                                    st.markdown(f"**Added**: {provider.created_at.strftime('%Y-%m-%d')}")
                                    st.markdown(f"**Updated**: {provider.updated_at.strftime('%Y-%m-%d')}")
                        with col2:
                            if st.button("Edit", key=f"edit_{provider.id}"):
                                st.session_state["selected_provider_id"] = provider.id
                                st.session_state["active_tab"] = 2
                                st.rerun()
        else:
            # Display as detailed list
            for provider in providers:
                with st.expander(f"{provider.name} ({provider.provider_type.value})"):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.markdown(f"**Description**: {provider.description}")
                        st.markdown(f"**Website**: [{provider.url}]({provider.url})")
                        if provider.github_url:
                            st.markdown(f"**GitHub**: [{provider.github_url}]({provider.github_url})")
                        if provider.docs_url:
                            st.markdown(f"**Documentation**: [{provider.docs_url}]({provider.docs_url})")
                        # Show version for frameworks
                        if provider.provider_type == ProviderType.FRAMEWORK and provider.version:
                            st.markdown(f"**Version**: {provider.version}")
                    with col2:
                        st.markdown(f"**ID**: `{provider.id}`")
                        if provider.support_email:
                            st.markdown(f"**Support Email**: {provider.support_email}")
                        if provider.support_url:
                            st.markdown(f"**Support URL**: [{provider.support_url}]({provider.support_url})")
                        st.markdown(f"**Added**: {provider.created_at.strftime('%Y-%m-%d')}")
                        st.markdown(f"**Updated**: {provider.updated_at.strftime('%Y-%m-%d')}")
                        
                        # Edit and delete buttons
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Edit", key=f"edit_exp_{provider.id}"):
                                st.session_state["selected_provider_id"] = provider.id
                                st.session_state["active_tab"] = 2
                                st.rerun()
                        with col2:
                            if st.button("Delete", key=f"delete_{provider.id}"):
                                # Check if provider has any agents
                                agents_with_provider = [a for a in db.get_all_agents() if a.provider_id == provider.id]
                                
                                if agents_with_provider:
                                    st.error(f"Cannot delete provider: {len(agents_with_provider)} agents are using this provider.")
                                    st.markdown("Please remove or reassign these agents first:")
                                    for agent in agents_with_provider:
                                        st.markdown(f"- {agent.name}")
                                else:
                                    if db.delete_provider(provider.id):
                                        st.success("Provider deleted!")
                                        st.rerun()
                                    else:
                                        st.error("Failed to delete provider.")

# Function to display provider form fields
def provider_form_fields(editing_provider=None):
    """Display form fields for adding/editing a provider."""
    # Basic information
    name = st.text_input("Name", value=editing_provider.name if editing_provider else "")
    
    # Provider type selection
    provider_type = st.selectbox(
        "Type", 
        options=[p.value for p in ProviderType],
        index=list(ProviderType).index(editing_provider.provider_type) if editing_provider else 0
    )
    
    description = st.text_area("Description", value=editing_provider.description if editing_provider else "")
    url = url_input("Website URL", value=editing_provider.url if editing_provider else None)
    
    # Show version field for frameworks
    version = None
    if provider_type == ProviderType.FRAMEWORK.value:
        version = st.text_input(
            "Version", 
            value=editing_provider.version if editing_provider and editing_provider.version else ""
        )
    
    # Additional URLs and contact info
    col1, col2 = st.columns(2)
    with col1:
        github_url = url_input(
            "GitHub URL (optional)", 
            value=editing_provider.github_url if editing_provider else None
        )
        docs_url = url_input(
            "Documentation URL (optional)", 
            value=editing_provider.docs_url if editing_provider else None
        )
    with col2:
        logo_url = url_input(
            "Logo URL (optional)", 
            value=editing_provider.logo_url if editing_provider else None
        )
        support_email = st.text_input(
            "Support Email (optional)", 
            value=editing_provider.support_email if editing_provider else ""
        )
        support_url = url_input(
            "Support URL (optional)", 
            value=editing_provider.support_url if editing_provider else None
        )
    
    # Return all form values
    return {
        "name": name,
        "provider_type": provider_type,
        "description": description,
        "url": url,
        "version": version,
        "github_url": github_url,
        "docs_url": docs_url,
        "logo_url": logo_url,
        "support_email": support_email,
        "support_url": support_url
    }

# Function to save provider data
def save_provider_data(form_data, editing_provider=None):
    """Save the provider data from form submission."""
    try:
        # Create provider data dictionary
        provider_data = {
            "name": form_data["name"],
            "description": form_data["description"],
            "url": form_data["url"],
            "provider_type": form_data["provider_type"],
            "github_url": form_data["github_url"],
            "docs_url": form_data["docs_url"],
            "logo_url": form_data["logo_url"],
            "support_email": form_data["support_email"],
            "support_url": form_data["support_url"]
        }
        
        # Add version for frameworks
        if form_data["provider_type"] == ProviderType.FRAMEWORK.value and form_data["version"]:
            provider_data["version"] = form_data["version"]
        
        # Add ID and timestamps for editing
        if editing_provider:
            provider_data["id"] = editing_provider.id
            provider_data["created_at"] = editing_provider.created_at
            provider_data["updated_at"] = datetime.datetime.now()
            
            provider = Provider(**provider_data)
            db.update_provider(provider)
            return True, f"Provider '{form_data['name']}' updated successfully!"
        else:
            provider = Provider(**provider_data)
            db.add_provider(provider)
            return True, f"Provider '{form_data['name']}' added successfully!"
    except Exception as e:
        return False, f"Error saving provider: {str(e)}"

# Tab 2: Add Provider
with tab2:
    st.header("Add New Provider")
    
    with st.form("add_provider_form"):
        form_data = provider_form_fields()
        
        # Form submission
        submitted = st.form_submit_button("Add Provider")
        if submitted:
            if not form_data["name"] or not form_data["description"] or not form_data["url"]:
                st.error("Name, description, and URL are required fields!")
            else:
                success, message = save_provider_data(form_data)
                if success:
                    st.success(message)
                    # Redirect to list view
                    st.session_state["active_tab"] = 0
                    st.rerun()
                else:
                    st.error(message)

# Tab 3: Edit Provider
with tab3:
    if editing_provider:
        st.header(f"Edit Provider: {editing_provider.name}")
        
        # Cancel editing button
        if st.button("Cancel Editing"):
            st.session_state.pop("selected_provider_id", None)
            st.rerun()
        
        with st.form("edit_provider_form"):
            form_data = provider_form_fields(editing_provider)
            
            # Form submission
            submitted = st.form_submit_button("Update Provider")
            if submitted:
                if not form_data["name"] or not form_data["description"] or not form_data["url"]:
                    st.error("Name, description, and URL are required fields!")
                else:
                    success, message = save_provider_data(form_data, editing_provider)
                    if success:
                        st.success(message)
                        # Clear session state and redirect to list view
                        st.session_state.pop("selected_provider_id", None)
                        st.session_state["active_tab"] = 0
                        st.rerun()
                    else:
                        st.error(message)
    else:  # No editing provider selected
        st.info("Select a provider from the 'Browse Providers' tab to edit.")
        
        # Option to go back to list view
        if st.button("Back to Provider List"):
            st.session_state["active_tab"] = 0
            st.rerun()