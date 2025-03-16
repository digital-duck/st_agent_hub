import json
import os
from typing import List, Optional, Dict, Any
from schema import AgentMetadata, Provider


class JSONDatabase:
    """A simple JSON-based database for storing Agent Hub data."""
    
    def __init__(self, data_dir: str = "../data"):
        self.data_dir = data_dir
        self.providers_file = os.path.join(data_dir, "providers.json")
        self.agents_file = os.path.join(data_dir, "agents.json")
        
        # Initialize data storage
        self.providers: Dict[str, Provider] = {}
        self.agents: Dict[str, AgentMetadata] = {}
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Load existing data if available
        self._load_data()
    
    def _load_data(self):
        """Load data from JSON files if they exist."""
        # Load providers
        if os.path.exists(self.providers_file):
            with open(self.providers_file, 'r') as f:
                providers_data = json.load(f)
                for provider_dict in providers_data:
                    provider = Provider(**provider_dict)
                    self.providers[provider.id] = provider
        
        # Load agents
        if os.path.exists(self.agents_file):
            with open(self.agents_file, 'r') as f:
                agents_data = json.load(f)
                for agent_dict in agents_data:
                    agent = AgentMetadata(**agent_dict)
                    self.agents[agent.id] = agent
    
    def _save_data(self):
        """Save all data to JSON files."""
        # Save providers
        with open(self.providers_file, 'w') as f:
            json.dump([provider.dict() for provider in self.providers.values()], f, default=str, indent=2)
        
        # Save agents
        with open(self.agents_file, 'w') as f:
            json.dump([agent.dict() for agent in self.agents.values()], f, default=str, indent=2)
    
    # Provider operations
    def add_provider(self, provider: Provider) -> Provider:
        """Add a new provider to the database."""
        self.providers[provider.id] = provider
        self._save_data()
        return provider
    
    def get_provider(self, provider_id: str) -> Optional[Provider]:
        """Get a provider by ID."""
        return self.providers.get(provider_id)
    
    def get_all_providers(self) -> List[Provider]:
        """Get all providers."""
        return list(self.providers.values())
    
    def get_providers_by_type(self, provider_type: str) -> List[Provider]:
        """Get providers filtered by type."""
        return [p for p in self.providers.values() if p.provider_type == provider_type]
    
    def update_provider(self, provider: Provider) -> Provider:
        """Update an existing provider."""
        if provider.id not in self.providers:
            raise ValueError(f"Provider with ID {provider.id} not found")
        self.providers[provider.id] = provider
        self._save_data()
        return provider
    
    def delete_provider(self, provider_id: str) -> bool:
        """Delete a provider by ID."""
        if provider_id not in self.providers:
            return False
        del self.providers[provider_id]
        self._save_data()
        return True
    
    # Agent operations
    def add_agent(self, agent: AgentMetadata) -> AgentMetadata:
        """Add a new agent to the database."""
        # Link provider object
        if agent.provider_id in self.providers:
            agent.provider = self.providers[agent.provider_id]
        
        self.agents[agent.id] = agent
        self._save_data()
        return agent
    
    def get_agent(self, agent_id: str) -> Optional[AgentMetadata]:
        """Get an agent by ID."""
        return self.agents.get(agent_id)
    
    def get_all_agents(self) -> List[AgentMetadata]:
        """Get all agents."""
        return list(self.agents.values())
    
    def update_agent(self, agent: AgentMetadata) -> AgentMetadata:
        """Update an existing agent."""
        if agent.id not in self.agents:
            raise ValueError(f"Agent with ID {agent.id} not found")
        
        # Link provider object
        if agent.provider_id in self.providers:
            agent.provider = self.providers[agent.provider_id]
        
        self.agents[agent.id] = agent
        self._save_data()
        return agent
    
    def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent by ID."""
        if agent_id not in self.agents:
            return False
        del self.agents[agent_id]
        self._save_data()
        return True
    
    def search_agents(self, query: str) -> List[AgentMetadata]:
        """Search agents by name or description."""
        query = query.lower()
        results = []
        
        for agent in self.agents.values():
            if query in agent.name.lower() or query in agent.description.lower():
                results.append(agent)
        
        return results
    
    def filter_agents(self, 
                     provider_id: Optional[str] = None,
                     domains: Optional[List[str]] = None,
                     features: Optional[Dict[str, Any]] = None) -> List[AgentMetadata]:
        """Filter agents by various criteria."""
        results = list(self.agents.values())
        
        if provider_id:
            results = [agent for agent in results if agent.provider_id == provider_id]
        
        if domains:
            results = [agent for agent in results if any(domain in agent.domains for domain in domains)]
        
        if features:
            filtered_results = []
            for agent in results:
                match = True
                for key, value in features.items():
                    if hasattr(agent.features, key):
                        agent_value = getattr(agent.features, key)
                        if isinstance(agent_value, list):
                            if not any(v in agent_value for v in value):
                                match = False
                                break
                        elif agent_value != value:
                            match = False
                            break
                if match:
                    filtered_results.append(agent)
            results = filtered_results
        
        return results