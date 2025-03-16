from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
import uuid


class MemoryType(str, Enum):
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    NONE = "none"


class PlanningCapability(str, Enum):
    NONE = "none"
    BASIC = "basic"
    ADVANCED = "advanced"
    RECURSIVE = "recursive"
    HIERARCHICAL = "hierarchical"


class ToolUseCapability(str, Enum):
    NONE = "none"
    PREDEFINED = "predefined"
    DYNAMIC = "dynamic"
    TOOL_CREATION = "tool_creation"


class Provider(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    url: HttpUrl
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    logo_url: Optional[HttpUrl] = None
    github_url: Optional[HttpUrl] = None
    docs_url: Optional[HttpUrl] = None
    support_email: Optional[str] = None
    support_url: Optional[HttpUrl] = None


class Framework(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    url: HttpUrl
    github_url: Optional[HttpUrl] = None  # Make sure these optional fields are defined
    docs_url: Optional[HttpUrl] = None    # This is missing in your current schema
    version: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


class LLMSupport(BaseModel):
    model_name: str
    provider: str  # e.g., OpenAI, Anthropic, etc.
    min_version: Optional[str] = None
    notes: Optional[str] = None
    performance_rating: Optional[int] = None  # 1-5 scale


class VectorStore(BaseModel):
    name: str
    provider: Optional[str] = None
    url: Optional[HttpUrl] = None
    description: Optional[str] = None
    supported_dimensions: Optional[List[int]] = None
    notes: Optional[str] = None


class MemoryStore(BaseModel):
    name: str
    type: MemoryType
    provider: Optional[str] = None
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


class AgentDomain(str, Enum):
    GENERAL = "general"
    CUSTOMER_SERVICE = "customer_service"
    DATA_ANALYSIS = "data_analysis"
    CREATIVE = "creative"
    CODING = "coding"
    RESEARCH = "research"
    EDUCATION = "education"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    LEGAL = "legal"
    OTHER = "other"


class AgentMetadata(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    version: str
    provider_id: str
    provider: Optional[Provider] = None  # Populated from provider_id
    framework_id: Optional[str] = None
    framework: Optional[Framework] = None  # Populated from framework_id
    
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