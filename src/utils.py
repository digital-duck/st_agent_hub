import streamlit as st

# Common utility functions that can be shared across pages
def url_input(label, key=None, value=None):
    """Handle URL input with validation"""
    url = st.text_input(label, value=value, key=key)
    if url and not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url if url else None

# Function to get provider selection options
def get_provider_options(db, filter_type=None, include_none=True):
    """Get provider selection options with proper formatting.
    
    Args:
        db: Database instance
        filter_type: Optional ProviderType to filter providers
        include_none: Whether to include a "None" option
        
    Returns:
        Dictionary of {id: display_name} for providers
    """
    if filter_type:
        providers = db.get_providers_by_type(filter_type)
    else:
        providers = db.get_all_providers()
    
    # Create options dictionary
    options = {p.id: f"{p.name} ({p.provider_type.value})" for p in providers}
    
    # Add "None" option if requested
    if include_none:
        options["none"] = "None (Unspecified)"
        
    return options
