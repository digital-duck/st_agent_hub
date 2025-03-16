import os
import streamlit as st
from database import JSONDatabase
from schema import (
    Provider, AgentMetadata, AgentFeatures, 
    LLMSupport, VectorStore, MemoryStore, CodeSnippet,
    ResourceRequirement, MemoryType, PlanningCapability,
    ToolUseCapability, AgentDomain, ProviderType
)

# Common utility functions that can be shared across pages
def url_input(label, key=None, value=None):
    """Handle URL input with validation"""
    url = st.text_input(label, value=value, key=key)
    if url and not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url if url else None

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
        url="https://agno.app/",
        provider_type=ProviderType.COMPANY,
        github_url="https://github.com/agnoai/agno",
        docs_url="https://docs.agno.app/"
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
    
    db.add_provider(autogen_provider)
    db.add_provider(agno_provider)
    db.add_provider(llamaindex_framework)
    
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
            LLMSupport(model_name="GPT-4", provider="OpenAI", performance_rating=5),
            LLMSupport(model_name="Claude 3", provider="Anthropic", performance_rating=5)
        ],
        vector_stores=[
            VectorStore(name="FAISS", provider="Facebook", description="In-memory vector store optimized for similarity search")
        ],
        memory_stores=[
            MemoryStore(name="Redis", type=MemoryType.LONG_TERM, description="Distributed key-value store with persistence options")
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

# For direct execution of app.py
if __name__ == "__main__":
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Seed initial data
    seed_data()
    
    # Run the main page
    import AI_Agent_Hub
    AI_Agent_Hub.main()