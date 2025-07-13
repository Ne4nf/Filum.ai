"""
Matching Engine for Pain Point to Solution Agent
Core algorithm to find and evaluate solution relevance
"""

from typing import List, Dict, Tuple, Optional
import re
import json
from pathlib import Path
import math

from models import (
    PainPointInput, 
    KnowledgeBase, 
    KnowledgeBaseFeature,
    Solution,
    FilumFeature,
    ExpectedOutcomes,
    ResourceRequirements
)


class MatchingEngine:
    """Engine to match pain points with Filum.ai features"""
    
    def __init__(self, knowledge_base_path: Optional[str] = None):
        """
        Initialize matching engine
        
        Args:
            knowledge_base_path: Path to knowledge base JSON file
        """
        self.knowledge_base: Optional[KnowledgeBase] = None
        self.features: List[KnowledgeBaseFeature] = []
        
        if knowledge_base_path:
            self.load_knowledge_base(knowledge_base_path)
    
    def load_knowledge_base(self, file_path: str) -> None:
        """Load knowledge base from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.knowledge_base = KnowledgeBase(**data)
            self.features = self.knowledge_base.features
            print(f"✅ Loaded {len(self.features)} features from knowledge base")
            
        except Exception as e:
            print(f"❌ Error loading knowledge base: {e}")
            raise
    
    def find_matching_solutions(
        self, 
        pain_point: PainPointInput, 
        max_solutions: int = 5
    ) -> List[Solution]:
        """
        Find solutions matching the pain point
        
        Args:
            pain_point: Input pain point from user
            max_solutions: Maximum number of solutions to return
            
        Returns:
            List of solutions sorted by relevance score
        """
        if not self.features:
            raise ValueError("Knowledge base not loaded. Call load_knowledge_base() first.")
        
        # Calculate relevance score for each feature
        feature_scores = []
        for feature in self.features:
            score = self._calculate_relevance_score(pain_point, feature)
            if score > 0.1:  # Only keep features with sufficient score
                feature_scores.append((feature, score))
        
        # Sort by score descending
        feature_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Convert to Solution objects
        solutions = []
        for i, (feature, score) in enumerate(feature_scores[:max_solutions]):
            solution = self._create_solution_from_feature(
                feature, 
                score, 
                f"solution_{i+1}",
                pain_point
            )
            solutions.append(solution)
        
        return solutions
    
    def _calculate_relevance_score(
        self, 
        pain_point: PainPointInput, 
        feature: KnowledgeBaseFeature
    ) -> float:
        """
        Calculate relevance score between pain point and feature
        Use simple but effective semantic matching
        
        Args:
            pain_point: Input pain point
            feature: Feature from knowledge base
            
        Returns:
            Score from 0.0 to 1.0
        """
        pain_text = pain_point.pain_point.description.lower()
        
        # Direct mapping of pain point patterns with solutions
        pain_solution_mapping = {
            # Customer Service & Support Issues
            'support_response_time': {
                'patterns': ['time', 'wait', 'response time', 'slow', 'support', 'reply'],
                'best_features': ['AI Inbox with Smart Routing', 'AI Customer Service'],
                'score_boost': 0.4
            },
            'support_overload': {
                'patterns': ['overload', 'overwhelm', 'volume', 'many', 'repetitive', 'repeat'],
                'best_features': ['AI Inbox with Smart Routing', 'AI Customer Service'],
                'score_boost': 0.4
            },
            
            # Feedback Collection Issues
            'feedback_collection': {
                'patterns': ['feedback', 'response', 'collect', 'survey', 'collection'],
                'best_features': ['Multi-Channel Surveys', 'Voice of Customer'],
                'score_boost': 0.4
            },
            
            # Data Analysis Issues
            'manual_analysis': {
                'patterns': ['manual', 'analysis', 'analysis', 'time-consuming', 'time consuming'],
                'best_features': ['AI-Powered Conversation Analysis', 'Customer Insights'],
                'score_boost': 0.4
            },
            
            # Customer Insights Issues
            'customer_understanding': {
                'patterns': ['dont understand', 'insight', 'needs', 'behavior', 'behavior', 'understand'],
                'best_features': ['Customer Journey Analytics', 'Customer Insights'],
                'score_boost': 0.4
            },
            
            # Customer Profile Issues
            'customer_history': {
                'patterns': ['history', 'history', 'profile', 'single view', 'unified', 'consolidated', 'view', 'interaction', 'contact again'],
                'best_features': ['Customer 360', 'Customer Profile'],
                'score_boost': 0.4
            }
        }
        
        base_score = 0.1  # Base score for all features
        feature_name = feature.feature_name
        
        # Check pain point patterns
        for pain_type, config in pain_solution_mapping.items():
            pattern_matches = sum(1 for pattern in config['patterns'] if pattern in pain_text)
            
            if pattern_matches > 0:
                # Check if this feature is a best match for this pain type
                if any(best_feature in feature_name for best_feature in config['best_features']):
                    base_score += config['score_boost'] * (pattern_matches / len(config['patterns']))
                else:
                    # Slight boost for related features
                    base_score += 0.1 * (pattern_matches / len(config['patterns']))
        
        # Additional scoring based on feature category
        category_boost = self._get_category_boost(pain_text, feature)
        base_score += category_boost
        
        # Context-based adjustments
        context_boost = self._get_context_boost(pain_point, feature)
        base_score += context_boost
        
        return min(base_score, 1.0)  # Cap at 1.0
    
    def _get_category_boost(self, pain_text: str, feature: KnowledgeBaseFeature) -> float:
        """Boost score based on category matching"""
        category = feature.category  # Use 'category' instead of 'feature_category'
        
        category_patterns = {
            'AI_CUSTOMER_SERVICE': ['support', 'agent', 'customer service', 'helpdesk'],
            'VOC': ['feedback', 'voice', 'survey', 'opinion'],
            'INSIGHTS': ['insight', 'analysis', 'data', 'report', 'analysis'],
            'CUSTOMER_360': ['profile', 'history', 'view', '360', 'unified'],
            'AI_AUTOMATION': ['automation', 'auto', 'workflow']
        }
        
        if hasattr(category, 'value'):
            category_value = category.value
        else:
            category_value = str(category)
        
        patterns = category_patterns.get(category_value, [])
        matches = sum(1 for pattern in patterns if pattern in pain_text)
        
        return min(0.3 * matches / len(patterns) if patterns else 0, 0.3)
    
    def _get_context_boost(self, pain_point: PainPointInput, feature: KnowledgeBaseFeature) -> float:
        """Boost score based on context (urgency, company size, etc.)"""
        boost = 0.0
        context = pain_point.pain_point.context
        
        if not context:
            return boost
        
        # Urgency boost - urgent problems need quick solutions
        if hasattr(context, 'urgency_level') and context.urgency_level:
            urgency = context.urgency_level.value if hasattr(context.urgency_level, 'value') else str(context.urgency_level)
            if urgency == 'high':
                # Prefer AI/automation solutions for urgent issues
                if 'AI' in feature.feature_name or 'Smart' in feature.feature_name:
                    boost += 0.1
        
        # Company size boost
        if hasattr(context, 'company_size') and context.company_size:
            size = context.company_size.value if hasattr(context.company_size, 'value') else str(context.company_size)
            if size in ['large', 'enterprise']:
                # Large companies benefit more from comprehensive solutions
                boost += 0.05
        
        return boost
    
    def _calculate_keyword_similarity(
        self, 
        pain_point: PainPointInput, 
        feature: KnowledgeBaseFeature
    ) -> float:
        """Calculate keyword similarity between pain point and feature"""
        # Extract keywords from pain point description
        pain_keywords = self._extract_keywords(pain_point.pain_point.description.lower())
        
        # Get all keywords from feature
        feature_keywords = []
        for pain_addressed in feature.pain_points_addressed:
            feature_keywords.extend([kw.lower() for kw in pain_addressed.keywords])
        
        if not feature_keywords:
            return 0.0
        
        # Calculate number of keyword matches
        matches = 0
        for pain_kw in pain_keywords:
            for feature_kw in feature_keywords:
                if pain_kw in feature_kw or feature_kw in pain_kw:
                    matches += 1
                    break
        
        # Normalize by number of pain keywords
        return matches / len(pain_keywords) if pain_keywords else 0.0
    
    def _calculate_category_alignment(
        self, 
        pain_point: PainPointInput, 
        feature: KnowledgeBaseFeature
    ) -> float:
        """Calculate category matching between pain point and feature"""
        pain_description = pain_point.pain_point.description.lower()
        
        # Mapping categories with keywords
        category_keywords = {
            'feedback_collection': ['feedback', 'survey'],
            'support_overload': ['support', 'agent', 'overload', 'volume'],
            'customer_visibility': ['profile', 'history', 'view', 'unified', 'single'],
            'journey_visibility': ['journey', 'touchpoint', 'experience', 'friction'],
            'data_analysis': ['analysis', 'insight', 'manual', 'data']
        }
        
        max_score = 0.0
        for pain_addressed in feature.pain_points_addressed:
            category = pain_addressed.pain_category
            if category in category_keywords:
                keywords = category_keywords[category]
                matches = sum(1 for kw in keywords if kw in pain_description)
                score = matches / len(keywords)
                max_score = max(max_score, score)
        
        return max_score
    
    def _calculate_context_fit(
        self, 
        pain_point: PainPointInput, 
        feature: KnowledgeBaseFeature
    ) -> float:
        """Calculate context matching (industry, company size, etc.)"""
        context = pain_point.pain_point.context
        if not context:
            return 0.5  # Neutral score if no context
        
        score = 0.0
        score_count = 0
        
        # Check industry match
        if context.industry:
            for pain_addressed in feature.pain_points_addressed:
                if context.industry in pain_addressed.business_contexts:
                    score += 1.0
                    score_count += 1
                    break
            if score_count == 0:
                score_count += 1  # Add neutral score
        
        # Check company size compatibility
        if context.company_size:
            # Features with high complexity match with large companies
            complexity_size_fit = {
                'low': ['startup', 'small'],
                'medium': ['small', 'medium', 'large'],
                'high': ['medium', 'large', 'enterprise']
            }
            
            complexity = feature.implementation.complexity.value
            if context.company_size.value in complexity_size_fit.get(complexity, []):
                score += 1.0
            else:
                score += 0.3  # Partial match
            score_count += 1
        
        # Check urgency vs complexity
        if context.urgency_level:
            urgency = context.urgency_level.value
            complexity = feature.implementation.complexity.value
            
            # High urgency needs low complexity
            urgency_complexity_fit = {
                'high': {'low': 1.0, 'medium': 0.6, 'high': 0.3},
                'medium': {'low': 0.8, 'medium': 1.0, 'high': 0.7},
                'low': {'low': 0.6, 'medium': 0.8, 'high': 1.0}
            }
            
            score += urgency_complexity_fit.get(urgency, {}).get(complexity, 0.5)
            score_count += 1
        
        return score / score_count if score_count > 0 else 0.5
    
    def _calculate_capability_alignment(
        self, 
        pain_point: PainPointInput, 
        feature: KnowledgeBaseFeature
    ) -> float:
        """Calculate capability matching with requirements"""
        pain_description = pain_point.pain_point.description.lower()
        affected_areas = pain_point.pain_point.affected_areas
        
        capability_score = 0.0
        total_capabilities = len(feature.capabilities)
        
        if total_capabilities == 0:
            return 0.0
        
        for capability in feature.capabilities:
            cap_description = capability.description.lower()
            cap_name = capability.capability_name.lower()
            
            # Check keyword overlap
            capability_keywords = self._extract_keywords(cap_description + " " + cap_name)
            pain_keywords = self._extract_keywords(pain_description)
            
            matches = sum(1 for pain_kw in pain_keywords 
                         for cap_kw in capability_keywords 
                         if pain_kw in cap_kw or cap_kw in pain_kw)
            
            if matches > 0:
                capability_score += 1.0
            
            # Check use cases alignment
            for use_case in capability.use_cases:
                use_case_lower = use_case.lower()
                for area in affected_areas:
                    if area.lower() in use_case_lower:
                        capability_score += 0.5
                        break
        
        return min(capability_score / total_capabilities, 1.0)
    
    def _calculate_complexity_fit(
        self, 
        pain_point: PainPointInput, 
        feature: KnowledgeBaseFeature
    ) -> float:
        """Calculate complexity matching with user constraints"""
        preferences = pain_point.preferences
        context = pain_point.pain_point.context
        
        if not preferences and not context:
            return 0.7  # Neutral score
        
        complexity = feature.implementation.complexity.value
        score = 0.7  # Base score
        
        # Check urgency vs complexity
        if context and context.urgency_level:
            urgency = context.urgency_level.value
            if urgency == 'high' and complexity == 'low':
                score = 1.0
            elif urgency == 'high' and complexity == 'high':
                score = 0.3
            elif urgency == 'medium' and complexity == 'medium':
                score = 1.0
        
        # Check timeline preferences
        if preferences and preferences.implementation_timeline:
            timeline = preferences.implementation_timeline.lower()
            if ('quick' in timeline or 'fast' in timeline) and complexity == 'high':
                score *= 0.5
            elif ('long' in timeline or 'detailed' in timeline) and complexity == 'low':
                score *= 0.8
        
        return score
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        # Remove stop words and special characters
        stop_words = {
            'and', 'or', 'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with'
        }
        
        # Extract words and normalize
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        
        return list(set(keywords))  # Remove duplicates
    
    def _create_solution_from_feature(
        self, 
        feature: KnowledgeBaseFeature, 
        relevance_score: float,
        solution_id: str,
        pain_point: PainPointInput
    ) -> Solution:
        """Create Solution object from KnowledgeBaseFeature"""
        
        # Create FilumFeature
        filum_feature = FilumFeature(
            feature_category=feature.category,
            feature_name=feature.feature_name,
            feature_description=feature.description.detailed
        )
        
        # Generate implementation steps
        implementation_steps = self._generate_implementation_steps(feature, pain_point)
        
        # Generate expected outcomes
        expected_outcomes = ExpectedOutcomes(
            short_term=feature.benefits.quantitative[:2] if feature.benefits.quantitative else [],
            long_term=feature.benefits.qualitative[:2] if feature.benefits.qualitative else []
        )
        
        # Generate resource requirements
        resource_requirements = ResourceRequirements(
            technical=", ".join(feature.implementation.resources_needed[:2]),
            training="Training for team to use new features",
            ongoing_maintenance="Regular monitoring and optimization"
        )
        
        # Generate how it helps
        how_it_helps = self._generate_how_it_helps(feature, pain_point)
        
        return Solution(
            solution_id=solution_id,
            solution_name=f"{feature.feature_name} Solution",
            filum_features=[filum_feature],
            how_it_helps=how_it_helps,
            implementation_steps=implementation_steps,
            expected_outcomes=expected_outcomes,
            relevance_score=round(relevance_score, 2),
            complexity_level=feature.implementation.complexity,
            estimated_setup_time=feature.implementation.setup_time,
            resource_requirements=resource_requirements,
            success_metrics=self._generate_success_metrics(feature),
            related_case_studies=[story.challenge + " -> " + story.results 
                                for story in feature.success_stories[:1]]
        )
    
    def _generate_implementation_steps(
        self, 
        feature: KnowledgeBaseFeature, 
        pain_point: PainPointInput
    ) -> List[str]:
        """Generate implementation steps for solution"""
        steps = [
            "Analyze current requirements and define specific objectives",
            f"Set up {feature.feature_name} with matching configuration",
            "Integrate with existing systems (CRM, database, etc.)",
            "Train team on how to use the new feature",
            "Pilot test with small customer group",
            "Monitor results and optimize configuration",
            "Deploy full-scale and track metrics"
        ]
        
        # Customize based on feature type
        if "survey" in feature.feature_name.lower():
            steps.insert(2, "Design survey templates and matching questions")
        elif "ai" in feature.feature_name.lower():
            steps.insert(2, "Train AI model with company data")
        elif "analysis" in feature.feature_name.lower():
            steps.insert(2, "Prepare and clean data sources")
        
        return steps[:5]  # Limit to 5 steps
    
    def _generate_how_it_helps(
        self, 
        feature: KnowledgeBaseFeature, 
        pain_point: PainPointInput
    ) -> str:
        """Generate explanation of how feature helps solve the pain point"""
        pain_desc = pain_point.pain_point.description.lower()
        
        # Template-based generation
        if "feedback" in pain_desc or "survey" in pain_desc:
            return f"{feature.feature_name} helps automate the feedback collection process across multiple channels, increasing response rates and improving data quality."
        elif "support" in pain_desc or "agent" in pain_desc:
            return f"{feature.feature_name} reduces workload for human agents by automatically handling simple queries and routing complex ones to the right person."
        elif "analysis" in pain_desc or "analytics" in pain_desc:
            return f"{feature.feature_name} automates the data analysis process, helping extract insights quickly and accurately."
        elif "journey" in pain_desc or "experience" in pain_desc:
            return f"{feature.feature_name} provides complete visibility into customer journeys, helping identify friction points and optimize experiences."
        else:
            return f"{feature.feature_name} {feature.description.short}"
    
    def _generate_success_metrics(self, feature: KnowledgeBaseFeature) -> List[str]:
        """Generate success metrics for solution"""
        base_metrics = [
            "Customer Satisfaction Score (CSAT)",
            "Implementation Timeline Adherence",
            "User Adoption Rate"
        ]
        
        # Add feature-specific metrics
        feature_name = feature.feature_name.lower()
        if "survey" in feature_name:
            base_metrics.extend(["Survey Response Rate", "Data Quality Score"])
        elif "ai" in feature_name or "automation" in feature_name:
            base_metrics.extend(["Automation Rate", "Response Time Improvement"])
        elif "analysis" in feature_name:
            base_metrics.extend(["Insight Discovery Rate", "Analysis Time Reduction"])
        elif "engagement" in feature_name:
            base_metrics.extend(["Engagement Rate", "Conversion Rate"])
        
        return base_metrics[:5]  # Limit to 5 metrics
