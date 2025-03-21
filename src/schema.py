from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
import uuid


class MemoryType(str, Enum):
    NONE = "none"                # No memory capability or undefined
    SHORT_TERM = "short_term"    # Temporary, limited storage (e.g., conversation context)
    LONG_TERM = "long_term"      # Persistent storage across sessions
    EPISODIC = "session"         # Memory of session based memory
    SEMANTIC = "semantic"        # Conceptual knowledge and factual information
    OTHER = "other"              # Defined but outside current categories


class PlanningCapability(str, Enum):
    NONE = "none"                # No planning capability or undefined
    BASIC = "basic"              # Simple, linear planning
    ADVANCED = "advanced"        # Complex planning with contingencies
    RECURSIVE = "recursive"      # Self-referential planning where agent plans about its own plans
    HIERARCHICAL = "hierarchical"# Multi-level planning with different abstractions at each level
    OTHER = "other"              # Defined but outside current categories


class ToolUseCapability(str, Enum):
    NONE = "none"                # No tool use capability or undefined
    PREDEFINED = "predefined"    # Can use specific, pre-configured tools
    DYNAMIC = "dynamic"          # Can adapt to and use new tools at runtime
    TOOL_CREATION = "tool_creation"  # Can create new tools/functions
    OTHER = "other"              # Defined but outside current categories


class ProviderType(str, Enum):
    NONE = "none"                # No provider information or undefined
    COMPANY = "company"          # Commercial organization (Microsoft, Anthropic)
    FRAMEWORK = "framework"      # Software framework (LlamaIndex, LangChain)
    OPEN_SOURCE = "open_source"  # Open source project (AG2, agno)
    RESEARCH = "research"        # Research institution/lab (Camel)
    OTHER = "other"              # Defined but outside current categories


class AgentDomain(str, Enum):
    NONE = "none"                # No specific domain or undefined
    GENERAL = "general"          # General-purpose agent
    CUSTOMER_SERVICE = "customer_service"
    DATA_ANALYSIS = "data_analysis"
    CREATIVE = "creative"
    CODING = "coding"
    RESEARCH = "research"
    EDUCATION = "education"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    LEGAL = "legal"
    OTHER = "other"              # Defined but outside current categories


class Provider(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    url: HttpUrl
    provider_type: ProviderType = ProviderType.COMPANY   # Indicates if this is a company or framework
    version: Optional[str] = None                        # For frameworks
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    logo_url: Optional[HttpUrl] = None
    github_url: Optional[HttpUrl] = None
    docs_url: Optional[HttpUrl] = None
    support_email: Optional[str] = None
    support_url: Optional[HttpUrl] = None


class LLMSupport(BaseModel):
    model_name: str
    provider_id: Optional[str] = None
    provider: Optional[Provider] = None  # Populated from provider_id
    min_version: Optional[str] = None
    notes: Optional[str] = None
    performance_rating: Optional[int] = None  # 1-5 scale


class VectorStore(BaseModel):
    name: str
    provider_id: Optional[str] = None
    provider: Optional[Provider] = None  # Populated from provider_id
    url: Optional[HttpUrl] = None
    description: Optional[str] = None
    supported_dimensions: Optional[List[int]] = None
    notes: Optional[str] = None


class MemoryStore(BaseModel):
    name: str
    type: MemoryType
    provider_id: Optional[str] = None
    provider: Optional[Provider] = None  # Populated from provider_id
    url: Optional[HttpUrl] = None
    description: Optional[str] = None
    notes: Optional[str] = None


class CodeSnippet(BaseModel):
    language: str
    code: str
    description: str
    import_requirements: Optional[List[str]] = None


class AgentFeatures(BaseModel):
    planning: PlanningCapability = PlanningCapability.NONE
    memory: List[MemoryType] = [MemoryType.NONE]
    tool_use: ToolUseCapability = ToolUseCapability.NONE
    multi_agent_collaboration: bool = False
    human_in_the_loop: bool = False
    reasoning_frameworks: List[str] = []  # e.g., ReAct, CoT, ToT
    autonomous: bool = False
    fine_tuning_support: bool = False
    streaming_support: bool = False
    supports_vision: bool = False
    supports_audio: bool = False
    custom_features: Dict[str, Any] = {}


class ResourceRequirement(BaseModel):
    min_cpu: Optional[str] = None
    recommended_cpu: Optional[str] = None
    min_ram: Optional[str] = None
    recommended_ram: Optional[str] = None
    gpu_required: bool = False
    recommended_gpu: Optional[str] = None
    estimated_cost_per_hour: Optional[float] = None
    notes: Optional[str] = None



class AgentMetadata(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    version: str
    provider_id: str
    provider: Optional[Provider] = None  # Populated from provider_id
    
    # Core capabilities
    features: AgentFeatures
    
    # Technical details
    supported_llms: List[LLMSupport] = []
    vector_stores: List[VectorStore] = []
    memory_stores: List[MemoryStore] = []
    resource_requirements: ResourceRequirement = ResourceRequirement()
    
    # Usage information
    domains: List[AgentDomain] = [AgentDomain.GENERAL]
    code_snippets: List[CodeSnippet] = []
    example_prompts: List[str] = []
    
    # Metadata
    tags: List[str] = []
    github_url: Optional[HttpUrl] = None
    docs_url: Optional[HttpUrl] = None
    demo_url: Optional[HttpUrl] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Community information
    star_rating: Optional[float] = None  # Average user rating
    review_count: int = 0
    installation_count: int = 0