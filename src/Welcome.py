import streamlit as st
import os
import sys

from database import JSONDatabase
from schema import (
    Provider, AgentMetadata, AgentFeatures, 
    LLMSupport, VectorStore, MemoryStore, CodeSnippet,
    ResourceRequirement, MemoryType, PlanningCapability,
    ToolUseCapability, AgentDomain, ProviderType
)


# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


from database import JSONDatabase
from schema import ProviderType

# Seed some initial data for demo purposes
def seed_data():
    """Seed the database with some initial data if empty."""
    db = JSONDatabase()
    
    # Only seed if no data exists
    if db.get_all_providers() or db.get_all_agents():
        return
    
    # Add providers (companies)
    autogen_provider = Provider(
        name="Microsoft AutoGen",
        description="AutoGen is a framework that enables the development of LLM applications using multiple agents that can converse with each other to solve tasks.",
        url="https://microsoft.github.io/autogen/",
        provider_type=ProviderType.COMPANY,
        github_url="https://github.com/microsoft/autogen",
        docs_url="https://microsoft.github.io/autogen/docs/Getting-Started",
        support_email="autogen-support@microsoft.com"
    )
    
    agno_provider = Provider(
        name="Agno (formerly phidata)",
        description="Agno is a platform for building, testing, and deploying AI agents with a focus on ease of use and enterprise-grade features.",
        url="https://docs.agno.com/",
        provider_type=ProviderType.COMPANY,
        github_url="https://github.com/agno-agi/agno",
        docs_url="https://docs.agno.com/"
    )
    
    # Add framework providers
    llamaindex_framework = Provider(
        name="LlamaIndex",
        description="LlamaIndex is a data framework for LLM applications to ingest, structure, and access private or domain-specific data.",
        url="https://www.llamaindex.ai/",
        provider_type=ProviderType.FRAMEWORK,
        version="0.10.x",
        github_url="https://github.com/run-llama/llama_index",
        docs_url="https://docs.llamaindex.ai/"
    )
    
    # Add LLM providers
    openai_provider = Provider(
        name="OpenAI",
        description="OpenAI is an AI research and deployment company dedicated to ensuring that artificial general intelligence benefits all of humanity.",
        url="https://openai.com/",
        provider_type=ProviderType.COMPANY,
        github_url="https://github.com/openai",
        docs_url="https://platform.openai.com/docs"
    )
    
    anthropic_provider = Provider(
        name="Anthropic",
        description="Anthropic is an AI safety company working to build reliable, interpretable, and steerable AI systems.",
        url="https://www.anthropic.com/",
        provider_type=ProviderType.COMPANY,
        docs_url="https://docs.anthropic.com/"
    )
    
    # Add vector store provider
    facebook_provider = Provider(
        name="Facebook",
        description="Meta (formerly Facebook) is a technology company focused on building products that facilitate connection and communication.",
        url="https://ai.meta.com/",
        provider_type=ProviderType.COMPANY,
        github_url="https://github.com/facebookresearch",
        docs_url="https://ai.meta.com/resources/"
    )
    
    # Add memory store provider
    redis_provider = Provider(
        name="Redis",
        description="Redis is an open source, in-memory data structure store used as a database, cache, message broker, and streaming engine.",
        url="https://redis.io/",
        provider_type=ProviderType.OPEN_SOURCE,
        github_url="https://github.com/redis/redis",
        docs_url="https://redis.io/docs/"
    )
    
    # Add all providers to the database
    db.add_provider(autogen_provider)
    db.add_provider(agno_provider)
    db.add_provider(llamaindex_framework)
    db.add_provider(openai_provider)
    db.add_provider(anthropic_provider)
    db.add_provider(facebook_provider)
    db.add_provider(redis_provider)
    
    # Sample agent for AutoGen
    autogen_agent = AgentMetadata(
        name="AutoGen Conversational Agent",
        description="A conversational agent built using Microsoft's AutoGen framework, capable of performing complex reasoning tasks through multi-agent collaboration.",
        version="0.2.0",
        provider_id=autogen_provider.id,
        features=AgentFeatures(
            planning=PlanningCapability.ADVANCED,
            memory=[MemoryType.SHORT_TERM, MemoryType.LONG_TERM],
            tool_use=ToolUseCapability.DYNAMIC,
            multi_agent_collaboration=True,
            human_in_the_loop=True,
            autonomous=True,
            reasoning_frameworks=["ReAct", "CoT"]
        ),
        supported_llms=[
            LLMSupport(
                model_name="GPT-4", 
                provider_id=openai_provider.id,
                performance_rating=5
            ),
            LLMSupport(
                model_name="Claude 3", 
                provider_id=anthropic_provider.id,
                performance_rating=5
            )
        ],
        vector_stores=[
            VectorStore(
                name="FAISS", 
                provider_id=facebook_provider.id,
                description="In-memory vector store optimized for similarity search"
            )
        ],
        memory_stores=[
            MemoryStore(
                name="Redis", 
                type=MemoryType.LONG_TERM,
                provider_id=redis_provider.id, 
                description="Distributed key-value store with persistence options"
            )
        ],
        domains=[AgentDomain.GENERAL, AgentDomain.CODING, AgentDomain.RESEARCH],
        code_snippets=[
            CodeSnippet(
                language="python",
                description="Basic AutoGen Agent Setup",
                code='''
from autogen import AssistantAgent, UserProxyAgent

# Create an assistant agent
assistant = AssistantAgent(
    name="assistant",
    llm_config={
        "model": "gpt-4",
        "api_key": os.environ.get("OPENAI_API_KEY"),
    }
)

# Create a user proxy agent
user_proxy = UserProxyAgent(
    name="user_proxy",
    human_input_mode="TERMINATE",
    max_consecutive_auto_reply=10,
)

# Start the conversation
user_proxy.initiate_chat(
    assistant,
    message="Help me solve the following problem: implement a quicksort algorithm in Python."
)
                ''',
                import_requirements=["autogen", "os"]
            )
        ],
        tags=["conversational", "coding", "multi-agent", "reasoning"],
        github_url="https://github.com/microsoft/autogen",
        docs_url="https://microsoft.github.io/autogen/docs/Use-Cases/agent_chat"
    )
    
    db.add_agent(autogen_agent)


def welcome():
    """Main entry point for the Streamlit app."""
    # Ensure data directory exists
    os.makedirs("../data", exist_ok=True)
    
    # Seed initial data
    seed_data()
    
    # Set page configuration
    st.set_page_config(
        page_title="AI Agent Hub",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize database
    db = JSONDatabase()
    
    # Display the home page
    st.header("👨‍👨 AI Agent Hub")
    st.markdown("""
    Welcome to AI Agent Hub - a central repository for discovering, comparing, and managing AI agents.
    
    ### Features:
    - Add and manage providers of AI agents (companies and frameworks)
    - Document agent capabilities and requirements
    - Search and filter agents by various criteria
    - Compare agents side-by-side
    
    ### Getting Started:
    1. Add providers using the **Providers** section
    2. Add agent metadata using the **Agents** section
    3. Browse and search for agents in the **Browse & Search** section
    4. Compare multiple agents in the **Compare Agents** section
    
    This application is designed to help you catalog and discover AI agents across different
    platforms and frameworks.
    """)
    
    # Display quick stats
    provider_counts = {}
    for provider in db.get_all_providers():
        provider_type = provider.provider_type.value
        provider_counts[provider_type] = provider_counts.get(provider_type, 0) + 1
    
    # Create a metric for total providers and a breakdown by type
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Providers", len(db.get_all_providers()))
        
        # Show provider breakdown if there are any providers
        if provider_counts:
            st.caption("Provider Types:")
            for ptype, count in provider_counts.items():
                st.caption(f"- {ptype.capitalize()}: {count}")
    
    with col2:
        st.metric("Agents", len(db.get_all_agents()))
        
        # Show agent domain breakdown if there are any agents
        if db.get_all_agents():
            # Count agents by domain
            domain_counts = {}
            for agent in db.get_all_agents():
                for domain in agent.domains:
                    domain_name = domain.value
                    domain_counts[domain_name] = domain_counts.get(domain_name, 0) + 1
            
            # Display domain counts
            st.caption("Agent Domains:")
            # Show top 3 domains at most
            for domain, count in list(sorted(domain_counts.items(), key=lambda x: x[1], reverse=True))[:3]:
                st.caption(f"- {domain.capitalize()}: {count}")
    
    # Display some featured providers
    st.subheader("Featured Providers")
    
    # Create columns for featured providers
    provider_cols = st.columns(3)
    
    # Get providers by different types for a balanced display
    companies = db.get_providers_by_type(ProviderType.COMPANY)[:1]
    frameworks = db.get_providers_by_type(ProviderType.FRAMEWORK)[:1]
    open_source = db.get_providers_by_type(ProviderType.OPEN_SOURCE)[:1]
    
    # Combine providers ensuring we have at most 3
    featured_providers = companies + frameworks + open_source
    featured_providers = featured_providers[:3]
    
    # Display featured providers
    for i, provider in enumerate(featured_providers):
        with provider_cols[i]:
            with st.container(border=True):
                st.subheader(provider.name)
                st.caption(f"Type: {provider.provider_type.value.capitalize()}")
                description = provider.description
                if len(description) > 150:
                    description = description[:150] + "..."
                st.write(description)
                
                # Add links
                links = []
                if provider.url:
                    links.append(f"[Website]({provider.url})")
                if provider.github_url:
                    links.append(f"[GitHub]({provider.github_url})")
                if provider.docs_url:
                    links.append(f"[Docs]({provider.docs_url})")
                    
                st.write(" | ".join(links))
    
    # Display some featured agents
    st.subheader("Featured Agents")
    
    # Create columns for featured agents
    agent_cols = st.columns(3)
    
    # Get all agents
    agents = db.get_all_agents()
    
    # Display up to 3 agents in columns
    for i, agent in enumerate(agents[:3]):
        with agent_cols[i]:
            with st.container(border=True):
                st.subheader(agent.name)
                
                # Get provider if available
                provider_name = "Unknown"
                provider_type = ""
                if agent.provider:
                    provider_name = agent.provider.name
                    provider_type = f" ({agent.provider.provider_type.value})"
                
                st.caption(f"Provider: {provider_name}{provider_type}")
                
                # Description
                description = agent.description
                if len(description) > 120:
                    description = description[:120] + "..."
                st.write(description)
                
                # Display some key features
                features_col1, features_col2 = st.columns(2)
                with features_col1:
                    st.write(f"**Planning:** {agent.features.planning.value}")
                    st.write(f"**Tool Use:** {agent.features.tool_use.value}")
                
                with features_col2:
                    # Get LLM support
                    llms = []
                    for llm in agent.supported_llms[:2]:  # Show max 2 LLMs
                        provider_name = llm.provider.name if llm.provider else "Unknown"
                        llms.append(f"{llm.model_name} ({provider_name})")
                    
                    if llms:
                        st.write("**LLMs:**")
                        for llm in llms:
                            st.write(f"- {llm}")
                
                # Show domains
                st.write("**Domains:**")
                domains_text = ", ".join([d.value for d in agent.domains])
                st.write(domains_text)
                
                # Add a View Details button
                if st.button("View Details", key=f"view_{agent.id}"):
                    # Store the selected agent ID in session state
                    st.session_state["selected_agent_id"] = agent.id
                    # Redirect to the Agents page
                    st.switch_page("pages/2_🤖_Agents.py")
                


if __name__ == "__main__":
    welcome()