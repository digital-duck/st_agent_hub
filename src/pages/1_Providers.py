import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional
import datetime

# Import our database and schema
from schema import Provider
from database import JSONDatabase
from app import url_input

# Set page configuration
st.set_page_config(
    page_title="AI Agent Hub - Providers",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
db = JSONDatabase()

# Page title
st.title("AI Agent Providers")

# Tabs for listing and adding providers
tab1, tab2 = st.tabs(["List Providers", "Add/Edit Provider"])

with tab1:
    providers = db.get_all_providers()
    if not providers:
        st.info("No providers added yet. Use the 'Add/Edit Provider' tab to add some.")
    else:
        for provider in providers:
            with st.expander(f"{provider.name}"):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"**Description**: {provider.description}")
                    st.markdown(f"**Website**: [{provider.url}]({provider.url})")
                    if provider.github_url:
                        st.markdown(f"**GitHub**: [{provider.github_url}]({provider.github_url})")
                    if provider.docs_url:
                        st.markdown(f"**Documentation**: [{provider.docs_url}]({provider.docs_url})")
                with col2:
                    st.markdown(f"**ID**: `{provider.id}`")
                    if provider.support_email:
                        st.markdown(f"**Support Email**: {provider.support_email}")
                    if provider.support_url:
                        st.markdown(f"**Support URL**: [{provider.support_url}]({provider.support_url})")
                    st.markdown(f"**Added**: {provider.created_at.strftime('%Y-%m-%d')}")
                    
                    # Edit and delete buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Edit", key=f"edit_{provider.id}"):
                            st.session_state["edit_provider"] = provider.id
                            st.rerun()
                    with col2:
                        if st.button("Delete", key=f"delete_{provider.id}"):
                            if db.delete_provider(provider.id):
                                st.success("Provider deleted!")
                                st.rerun()
                            else:
                                st.error("Failed to delete provider.")

with tab2:
    st.header("Add/Edit Provider")
    
    # Check if we're editing an existing provider
    editing_provider = None
    provider_id = st.session_state.get("edit_provider")
    if provider_id:
        editing_provider = db.get_provider(provider_id)
        st.info(f"Editing provider: {editing_provider.name}")
        # Clear the session state for future runs
        if st.button("Cancel Editing"):
            st.session_state.pop("edit_provider", None)
            st.rerun()
    
    # Provider form
    with st.form("provider_form"):
        name = st.text_input("Provider Name", value=editing_provider.name if editing_provider else "")
        description = st.text_area("Description", value=editing_provider.description if editing_provider else "")
        url = url_input("Website URL", value=editing_provider.url if editing_provider else None)
        github_url = url_input("GitHub URL (optional)", value=editing_provider.github_url if editing_provider else None)
        docs_url = url_input("Documentation URL (optional)", value=editing_provider.docs_url if editing_provider else None)
        logo_url = url_input("Logo URL (optional)", value=editing_provider.logo_url if editing_provider else None)
        support_email = st.text_input("Support Email (optional)", value=editing_provider.support_email if editing_provider else "")
        support_url = url_input("Support URL (optional)", value=editing_provider.support_url if editing_provider else None)
        
        submitted = st.form_submit_button("Save Provider")
        if submitted:
            if not name or not description or not url:
                st.error("Name, description, and URL are required!")
            else:
                try:
                    # Create or update provider
                    if editing_provider:
                        provider = Provider(
                            id=editing_provider.id,
                            name=name,
                            description=description,
                            url=url,
                            github_url=github_url,
                            docs_url=docs_url,
                            logo_url=logo_url,
                            support_email=support_email,
                            support_url=support_url,
                            created_at=editing_provider.created_at,
                            updated_at=datetime.datetime.now()
                        )
                        db.update_provider(provider)
                        st.success(f"Provider '{name}' updated successfully!")
                        # Clear the session state
                        st.session_state.pop("edit_provider", None)
                    else:
                        provider = Provider(
                            name=name,
                            description=description,
                            url=url,
                            github_url=github_url,
                            docs_url=docs_url,
                            logo_url=logo_url,
                            support_email=support_email,
                            support_url=support_url
                        )
                        db.add_provider(provider)
                        st.success(f"Provider '{name}' added successfully!")
                    
                    # Clear form
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving provider: {str(e)}")