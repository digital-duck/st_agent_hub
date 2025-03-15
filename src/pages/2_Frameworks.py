import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional
import datetime

# Import our database and schema
from schema import Framework
from database import JSONDatabase
from app import url_input

# Set page configuration
st.set_page_config(
    page_title="AI Agent Hub - Frameworks",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
db = JSONDatabase()

# Page title
st.title("AI Agent Frameworks")

# Tabs for listing and adding frameworks
tab1, tab2 = st.tabs(["List Frameworks", "Add/Edit Framework"])

with tab1:
    frameworks = db.get_all_frameworks()
    if not frameworks:
        st.info("No frameworks added yet. Use the 'Add/Edit Framework' tab to add some.")
    else:
        for framework in frameworks:
            with st.expander(f"{framework.name}"):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"**Description**: {framework.description}")
                    st.markdown(f"**Website**: [{framework.url}]({framework.url})")
                    if hasattr(framework, 'github_url') and framework.github_url:
                        st.markdown(f"**GitHub**: [{framework.github_url}]({framework.github_url})")
                    # Check if docs_url attribute exists before accessing it
                    if hasattr(framework, 'docs_url') and framework.docs_url:
                        st.markdown(f"**Documentation**: [{framework.docs_url}]({framework.docs_url})")
                with col2:
                    st.markdown(f"**ID**: `{framework.id}`")
                    if hasattr(framework, 'version') and framework.version:
                        st.markdown(f"**Version**: {framework.version}")
                    st.markdown(f"**Added**: {framework.created_at.strftime('%Y-%m-%d')}")
                    
                    # Edit and delete buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Edit", key=f"edit_{framework.id}"):
                            st.session_state["edit_framework"] = framework.id
                            st.rerun()
                    with col2:
                        if st.button("Delete", key=f"delete_{framework.id}"):
                            if db.delete_framework(framework.id):
                                st.success("Framework deleted!")
                                st.rerun()
                            else:
                                st.error("Failed to delete framework.")

with tab2:
    st.header("Add/Edit Framework")
    
    # Check if we're editing an existing framework
    editing_framework = None
    framework_id = st.session_state.get("edit_framework")
    if framework_id:
        editing_framework = db.get_framework(framework_id)
        st.info(f"Editing framework: {editing_framework.name}")
        # Clear the session state for future runs
        if st.button("Cancel Editing"):
            st.session_state.pop("edit_framework", None)
            st.rerun()
    
    # Framework form
    with st.form("framework_form"):
        name = st.text_input("Framework Name", value=editing_framework.name if editing_framework else "")
        description = st.text_area("Description", value=editing_framework.description if editing_framework else "")
        url = url_input("Website URL", value=editing_framework.url if editing_framework else None)
        github_url = url_input("GitHub URL (optional)", 
                            value=editing_framework.github_url if editing_framework and hasattr(editing_framework, 'github_url') else None)
        docs_url = url_input("Documentation URL (optional)", 
                           value=editing_framework.docs_url if editing_framework and hasattr(editing_framework, 'docs_url') else None)
        version = st.text_input("Version (optional)", 
                             value=editing_framework.version if editing_framework and hasattr(editing_framework, 'version') else "")
        
        submitted = st.form_submit_button("Save Framework")
        if submitted:
            if not name or not description or not url:
                st.error("Name, description, and URL are required!")
            else:
                try:
                    # Create framework dict with required fields
                    framework_data = {
                        "name": name,
                        "description": description,
                        "url": url
                    }
                    
                    # Add optional fields if they exist
                    if github_url:
                        framework_data["github_url"] = github_url
                    if docs_url:
                        framework_data["docs_url"] = docs_url
                    if version:
                        framework_data["version"] = version
                    
                    # Create or update framework
                    if editing_framework:
                        # Add ID and timestamps for update
                        framework_data["id"] = editing_framework.id
                        framework_data["created_at"] = editing_framework.created_at
                        framework_data["updated_at"] = datetime.datetime.now()
                        
                        # Create Framework object
                        framework = Framework(**framework_data)
                        db.update_framework(framework)
                        st.success(f"Framework '{name}' updated successfully!")
                        # Clear the session state
                        st.session_state.pop("edit_framework", None)
                    else:
                        # Create Framework object
                        framework = Framework(**framework_data)
                        db.add_framework(framework)
                        st.success(f"Framework '{name}' added successfully!")
                    
                    # Clear form
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving framework: {str(e)}")