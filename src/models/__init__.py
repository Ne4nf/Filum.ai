"""
Data models for Pain Point to Solution Agent
Define data structures for input, output and knowledge base
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class UrgencyLevel(str, Enum):
    """Urgency level of pain point"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class CompanySize(str, Enum):
    """Company scale"""

    STARTUP = "startup"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    ENTERPRISE = "enterprise"


class ComplexityLevel(str, Enum):
    """Implementation complexity level"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PricingTier(str, Enum):
    """Feature pricing tier"""

    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class FilumCategory(str, Enum):
    """Main categories of Filum.ai"""

    VOC = "VoC"
    AI_CUSTOMER_SERVICE = "AI Customer Service"
    INSIGHTS = "Insights"
    CUSTOMER_360 = "Customer 360"
    AI_AUTOMATION = "AI & Automation"


class PainPointContext(BaseModel):
    """Pain point context"""

    industry: Optional[str] = Field(None, description="Customer industry")
    company_size: Optional[CompanySize] = Field(None, description="Scale company")
    current_tools: Optional[List[str]] = Field(
        default_factory=list, description="Current tools"
    )
    urgency_level: Optional[UrgencyLevel] = Field(None, description="Urgency level")
    budget_range: Optional[str] = Field(None, description="Budget range")


class CurrentImpactMetrics(BaseModel):
    """Current impact metrics"""

    customer_satisfaction: Optional[str] = Field(
        None, description="Customer satisfaction score"
    )
    response_time: Optional[str] = Field(None, description="Response time")
    volume: Optional[str] = Field(None, description="Workload volume")
    cost: Optional[str] = Field(None, description="Current cost")
    efficiency: Optional[str] = Field(None, description="Efficiency")


class CurrentImpact(BaseModel):
    """Current impact of pain point"""

    description: str = Field(..., description="Impact description")
    metrics: Optional[CurrentImpactMetrics] = Field(
        default_factory=CurrentImpactMetrics
    )


class PainPointData(BaseModel):
    """Main pain point data"""

    description: str = Field(..., description="Detailed problem description")
    context: Optional[PainPointContext] = Field(default_factory=PainPointContext)
    affected_areas: List[str] = Field(
        default_factory=list, description="Affected areas"
    )
    current_impact: Optional[CurrentImpact] = Field(None, description="Current impact")


class UserPreferences(BaseModel):
    """User preferences"""

    solution_types: Optional[List[str]] = Field(
        default_factory=list, description="Preferred solution types"
    )
    implementation_timeline: Optional[str] = Field(
        None, description="Implementation timeline"
    )
    integration_requirements: Optional[str] = Field(
        None, description="Integration requirements"
    )


class PainPointInput(BaseModel):
    """Input schema cho agent"""

    pain_point: PainPointData
    preferences: Optional[UserPreferences] = Field(default_factory=UserPreferences)


class FilumFeature(BaseModel):
    """Information about a Filum.ai feature"""

    feature_category: FilumCategory = Field(..., description="Feature category")
    feature_name: str = Field(..., description="Feature name")
    feature_description: str = Field(..., description="Feature description")


class ExpectedOutcomes(BaseModel):
    """Expected results from solution"""

    short_term: List[str] = Field(
        default_factory=list, description="Short-term results"
    )
    long_term: List[str] = Field(default_factory=list, description="Long-term results")


class ResourceRequirements(BaseModel):
    """Resource requirements for implementation"""

    technical: Optional[str] = Field(None, description="Technical requirements")
    training: Optional[str] = Field(None, description="Required training")
    ongoing_maintenance: Optional[str] = Field(None, description="Ongoing maintenance")


class Solution(BaseModel):
    """A recommended solution"""

    solution_id: str = Field(..., description="Unique solution ID")
    solution_name: str = Field(..., description="Solution name")
    filum_features: List[FilumFeature] = Field(
        ..., description="Related Filum.ai features"
    )
    how_it_helps: str = Field(..., description="How solution helps solve the problem")
    implementation_steps: List[str] = Field(
        default_factory=list, description="Implementation steps"
    )
    expected_outcomes: Optional[ExpectedOutcomes] = Field(
        default_factory=ExpectedOutcomes
    )
    relevance_score: float = Field(..., ge=0, le=1, description="Matching score (0-1)")
    complexity_level: ComplexityLevel = Field(..., description="Complexity level")
    estimated_setup_time: Optional[str] = Field(
        None, description="Estimated setup time"
    )
    resource_requirements: Optional[ResourceRequirements] = Field(
        default_factory=ResourceRequirements
    )
    success_metrics: List[str] = Field(
        default_factory=list, description="Success metrics"
    )
    related_case_studies: Optional[List[str]] = Field(
        default_factory=list, description="Related case studies"
    )


class AlternativeApproach(BaseModel):
    """Alternative approach"""

    approach_name: str = Field(..., description="Approach name")
    description: str = Field(..., description="Approach description")
    pros_cons: Dict[str, List[str]] = Field(
        default_factory=dict, description="Pros and cons"
    )


class NextSteps(BaseModel):
    """Next steps"""

    immediate_actions: List[str] = Field(
        default_factory=list, description="Immediate actions"
    )
    consultation_needed: Optional[bool] = Field(
        None, description="Need additional consultation"
    )
    demo_requests: List[str] = Field(
        default_factory=list, description="Available demo requests"
    )


class PainPointAnalysis(BaseModel):
    """Results analysis pain point"""

    pain_point_summary: str = Field(..., description="Problem summary")
    key_challenges: List[str] = Field(
        default_factory=list, description="Key challenges"
    )
    impact_assessment: str = Field(..., description="Impact assessment")


class AgentOutput(BaseModel):
    """Output schema from agent"""

    analysis: PainPointAnalysis
    recommended_solutions: List[Solution]
    alternative_approaches: Optional[List[AlternativeApproach]] = Field(
        default_factory=list
    )
    next_steps: Optional[NextSteps] = Field(default_factory=NextSteps)


# Knowledge Base Models


class PainPointAddressed(BaseModel):
    """Pain point that feature can address"""

    pain_category: str = Field(..., description="Pain point category")
    keywords: List[str] = Field(default_factory=list, description="Related keywords")
    severity_levels: List[UrgencyLevel] = Field(
        default_factory=list, description="Severity levels"
    )
    business_contexts: List[str] = Field(
        default_factory=list, description="Business contexts"
    )


class FeatureCapability(BaseModel):
    """Feature capability"""

    capability_name: str = Field(..., description="Capability name")
    description: str = Field(..., description="Capability description")
    use_cases: List[str] = Field(default_factory=list, description="Use cases")


class IntegrationOptions(BaseModel):
    """Integration options"""

    channels: List[str] = Field(default_factory=list, description="Supported channels")
    third_party_tools: List[str] = Field(
        default_factory=list, description="Third-party tools"
    )
    apis_available: bool = Field(default=False, description="APIs available")


class ImplementationDetails(BaseModel):
    """Implementation details"""

    complexity: ComplexityLevel = Field(..., description="Complexity level")
    setup_time: str = Field(..., description="Setup time")
    resources_needed: List[str] = Field(
        default_factory=list, description="Required resources"
    )
    prerequisites: List[str] = Field(default_factory=list, description="Prerequisites")


class FeatureBenefits(BaseModel):
    """Feature benefits"""

    quantitative: List[str] = Field(
        default_factory=list, description="Quantitative benefits"
    )
    qualitative: List[str] = Field(
        default_factory=list, description="Qualitative benefits"
    )


class SuccessStory(BaseModel):
    """Case study success"""

    industry: str = Field(..., description="Industry")
    company_size: CompanySize = Field(..., description="Scale company")
    challenge: str = Field(..., description="Challenge")
    solution: str = Field(..., description="Solution")
    results: str = Field(..., description="Results")


class FeatureDescription(BaseModel):
    """Detailed feature description"""

    short: str = Field(..., description="Short description")
    detailed: str = Field(..., description="Detailed description")
    technical_specs: Optional[str] = Field(None, description="Technical specifications")


class KnowledgeBaseFeature(BaseModel):
    """Feature in knowledge base"""

    feature_id: str = Field(..., description="Unique ID")
    feature_name: str = Field(..., description="Feature name")
    category: FilumCategory = Field(..., description="Main category")
    subcategory: str = Field(..., description="Subcategory")
    description: FeatureDescription = Field(..., description="Feature description")
    pain_points_addressed: List[PainPointAddressed] = Field(default_factory=list)
    capabilities: List[FeatureCapability] = Field(default_factory=list)
    integration_options: Optional[IntegrationOptions] = Field(
        default_factory=IntegrationOptions
    )
    implementation: ImplementationDetails = Field(
        ..., description="Implementation details"
    )
    benefits: Optional[FeatureBenefits] = Field(default_factory=FeatureBenefits)
    success_stories: List[SuccessStory] = Field(default_factory=list)
    pricing_tier: Optional[PricingTier] = Field(None, description="Pricing tier")
    related_features: List[str] = Field(
        default_factory=list, description="Related features"
    )


class PainPointCategory(BaseModel):
    """Pain point category"""

    category_name: str = Field(..., description="Category name")
    subcategories: List[str] = Field(default_factory=list, description="Subcategories")
    common_keywords: List[str] = Field(
        default_factory=list, description="Common keywords"
    )
    indicators: List[str] = Field(
        default_factory=list, description="Recognition indicators"
    )


class PainPointTaxonomy(BaseModel):
    """Pain point classification"""

    categories: List[PainPointCategory] = Field(default_factory=list)


class BusinessContexts(BaseModel):
    """Business contexts"""

    industries: List[str] = Field(default_factory=list, description="Industries")
    company_sizes: List[CompanySize] = Field(
        default_factory=list, description="Company sizes"
    )
    business_models: List[str] = Field(
        default_factory=list, description="Business models"
    )


class KnowledgeBase(BaseModel):
    """Overall knowledge base"""

    features: List[KnowledgeBaseFeature] = Field(default_factory=list)
    pain_point_taxonomy: Optional[PainPointTaxonomy] = Field(
        default_factory=PainPointTaxonomy
    )
    business_contexts: Optional[BusinessContexts] = Field(
        default_factory=BusinessContexts
    )
