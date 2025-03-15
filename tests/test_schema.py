import unittest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from schema import Provider, AgentMetadata, AgentFeatures, MemoryType, PlanningCapability, ToolUseCapability, AgentDomain

class TestSchema(unittest.TestCase):
    def test_provider_creation(self):
        """Test that a Provider can be created."""
        provider = Provider(
            name="Test Provider",
            description="A test provider",
            url="https://example.com"
        )
        
        self.assertEqual(provider.name, "Test Provider")
        self.assertEqual(provider.description, "A test provider")
        self.assertEqual(str(provider.url), "https://example.com")
    
    def test_agent_metadata_creation(self):
        """Test that an AgentMetadata instance can be created with required fields."""
        agent = AgentMetadata(
            name="Test Agent",
            description="A test agent",
            version="1.0.0",
            provider_id="test-provider-id",
            features=AgentFeatures(
                planning=PlanningCapability.BASIC,
                memory=[MemoryType.SHORT_TERM],
                tool_use=ToolUseCapability.PREDEFINED
            ),
            domains=[AgentDomain.GENERAL]
        )
        
        self.assertEqual(agent.name, "Test Agent")
        self.assertEqual(agent.description, "A test agent")
        self.assertEqual(agent.version, "1.0.0")
        self.assertEqual(agent.provider_id, "test-provider-id")
        self.assertEqual(agent.features.planning, PlanningCapability.BASIC)
        self.assertEqual(agent.features.memory, [MemoryType.SHORT_TERM])
        self.assertEqual(agent.features.tool_use, ToolUseCapability.PREDEFINED)
        self.assertEqual(agent.domains, [AgentDomain.GENERAL])

if __name__ == '__main__':
    unittest.main()