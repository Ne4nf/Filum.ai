"""
Unit tests for Pain Point Agent
"""

import pytest
import json
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from models import PainPointInput, UrgencyLevel, CompanySize
from agent import PainPointAgent
from matching import MatchingEngine
from utils import (
    normalize_text, 
    extract_keywords, 
    validate_pain_point_input,
    calculate_text_similarity
)


class TestUtils:
    """Test utility functions"""
    
    def test_normalize_text(self):
        """Test text normalization"""
        # Test basic normalization
        assert normalize_text("  Hello WORLD  ") == "hello world"
        
        # Test Vietnamese text
        assert normalize_text("Hello World") == "hello world"
        
        # Test special characters
        assert normalize_text("Hello@#$%World!") == "hello world"
        
        # Test empty string
        assert normalize_text("") == ""
        assert normalize_text(None) == ""
    
    def test_extract_keywords(self):
        """Test keyword extraction"""
        text = "We have difficulty collecting customer feedback"
        keywords = extract_keywords(text)
        
        assert "difficulty" in keywords
        assert "collecting" in keywords
        assert "feedback" in keywords
        assert "customer" in keywords
        
        # Should not include stop words
        assert "we" not in keywords
        assert "have" not in keywords
        assert "in" not in keywords
    
    def test_calculate_text_similarity(self):
        """Test text similarity calculation"""
        text1 = "collect customer feedback"
        text2 = "gather customer responses"
        
        # Should have some similarity due to "feedback"
        similarity = calculate_text_similarity(text1, text2)
        assert 0.0 <= similarity <= 1.0
        
        # Identical texts
        assert calculate_text_similarity(text1, text1) == 1.0
        
        # Empty texts
        assert calculate_text_similarity("", "anything") == 0.0
    
    def test_validate_pain_point_input(self):
        """Test pain point input validation"""
        # Valid input
        valid_input = {
            "pain_point": {
                "description": "This is a valid pain point description with enough characters"
            }
        }
        errors = validate_pain_point_input(valid_input)
        assert len(errors) == 0
        
        # Missing pain_point
        invalid_input = {"something_else": "value"}
        errors = validate_pain_point_input(invalid_input)
        assert "Missing 'pain_point' field" in errors
        
        # Short description
        short_desc_input = {
            "pain_point": {
                "description": "Too short"
            }
        }
        errors = validate_pain_point_input(short_desc_input)
        assert any("at least 10 characters" in error for error in errors)


class TestModels:
    """Test Pydantic models"""
    
    def test_pain_point_input_creation(self):
        """Test PainPointInput model creation"""
        data = {
            "pain_point": {
                "description": "Test pain point description",
                "context": {
                    "industry": "E-commerce",
                    "company_size": "medium",
                    "urgency_level": "high"
                },
                "affected_areas": ["customer_service"]
            }
        }
        
        pain_point = PainPointInput(**data)
        assert pain_point.pain_point.description == "Test pain point description"
        assert pain_point.pain_point.context.industry == "E-commerce"
        assert pain_point.pain_point.context.company_size == CompanySize.MEDIUM
        assert pain_point.pain_point.context.urgency_level == UrgencyLevel.HIGH
    
    def test_pain_point_input_with_minimal_data(self):
        """Test PainPointInput with minimal required data"""
        data = {
            "pain_point": {
                "description": "Minimal pain point description"
            }
        }
        
        pain_point = PainPointInput(**data)
        assert pain_point.pain_point.description == "Minimal pain point description"
        assert pain_point.pain_point.context is not None  # Should have default
        assert pain_point.preferences is not None  # Should have default


class TestMatchingEngine:
    """Test MatchingEngine functionality"""
    
    @pytest.fixture
    def sample_knowledge_base_path(self, tmp_path):
        """Create a sample knowledge base for testing"""
        kb_data = {
            "features": [
                {
                    "feature_id": "test_survey",
                    "feature_name": "Multi-Channel Surveys",
                    "category": "VoC",
                    "subcategory": "Surveys",
                    "description": {
                        "short": "Survey tool",
                        "detailed": "Multi-channel survey tool for feedback collection",
                        "technical_specs": "REST API, webhooks"
                    },
                    "pain_points_addressed": [
                        {
                            "pain_category": "feedback_collection",
                            "keywords": ["survey", "feedback", "collection", "response"],
                            "severity_levels": ["medium", "high"],
                            "business_contexts": ["E-commerce", "Retail"]
                        }
                    ],
                    "capabilities": [
                        {
                            "capability_name": "Multi-channel distribution",
                            "description": "Send surveys via email, SMS, mobile",
                            "use_cases": ["Post-purchase feedback", "Customer satisfaction"]
                        }
                    ],
                    "integration_options": {
                        "channels": ["Email", "SMS", "Mobile"],
                        "third_party_tools": ["CRM"],
                        "apis_available": True
                    },
                    "implementation": {
                        "complexity": "medium",
                        "setup_time": "2-4 weeks",
                        "resources_needed": ["Technical integration"],
                        "prerequisites": ["Customer database"]
                    },
                    "benefits": {
                        "quantitative": ["Increase response rate 25%"],
                        "qualitative": ["Better customer insights"]
                    },
                    "success_stories": [],
                    "pricing_tier": "standard",
                    "related_features": []
                }
            ],
            "pain_point_taxonomy": {
                "categories": []
            },
            "business_contexts": {
                "industries": ["E-commerce", "Retail"],
                "company_sizes": ["small", "medium", "large"],
                "business_models": ["B2C"]
            }
        }
        
        kb_file = tmp_path / "test_kb.json"
        with open(kb_file, 'w', encoding='utf-8') as f:
            json.dump(kb_data, f)
        
        return str(kb_file)
    
    def test_matching_engine_initialization(self, sample_knowledge_base_path):
        """Test MatchingEngine initialization"""
        engine = MatchingEngine(sample_knowledge_base_path)
        assert engine.knowledge_base is not None
        assert len(engine.features) == 1
        assert engine.features[0].feature_name == "Multi-Channel Surveys"
    
    def test_find_matching_solutions(self, sample_knowledge_base_path):
        """Test finding matching solutions"""
        engine = MatchingEngine(sample_knowledge_base_path)
        
        pain_point_data = {
            "pain_point": {
                "description": "We need to collect customer feedback via surveys but response rate is low",
                "context": {
                    "industry": "E-commerce",
                    "company_size": "medium"
                },
                "affected_areas": ["customer_service"]
            }
        }
        
        pain_point = PainPointInput(**pain_point_data)
        solutions = engine.find_matching_solutions(pain_point, max_solutions=5)
        
        assert len(solutions) > 0
        assert solutions[0].relevance_score > 0
        assert "Multi-Channel Surveys" in solutions[0].solution_name


class TestPainPointAgent:
    """Test PainPointAgent main functionality"""
    
    @pytest.fixture
    def sample_agent(self, tmp_path):
        """Create PainPointAgent with sample knowledge base"""
        # Create minimal knowledge base
        kb_data = {
            "features": [
                {
                    "feature_id": "test_feature",
                    "feature_name": "Test Feature",
                    "category": "VoC",
                    "subcategory": "Test",
                    "description": {
                        "short": "Test feature",
                        "detailed": "A test feature for unit testing",
                        "technical_specs": "None"
                    },
                    "pain_points_addressed": [
                        {
                            "pain_category": "test_category",
                            "keywords": ["test", "feedback"],
                            "severity_levels": ["high"],
                            "business_contexts": ["E-commerce"]
                        }
                    ],
                    "capabilities": [],
                    "integration_options": {
                        "channels": [],
                        "third_party_tools": [],
                        "apis_available": False
                    },
                    "implementation": {
                        "complexity": "low",
                        "setup_time": "1 week",
                        "resources_needed": [],
                        "prerequisites": []
                    },
                    "benefits": {
                        "quantitative": [],
                        "qualitative": []
                    },
                    "success_stories": [],
                    "related_features": []
                }
            ],
            "pain_point_taxonomy": {"categories": []},
            "business_contexts": {
                "industries": [],
                "company_sizes": [],
                "business_models": []
            }
        }
        
        kb_file = tmp_path / "test_kb.json"
        with open(kb_file, 'w', encoding='utf-8') as f:
            json.dump(kb_data, f)
        
        return PainPointAgent(str(kb_file))
    
    def test_agent_initialization(self, sample_agent):
        """Test agent initialization"""
        assert sample_agent.matching_engine is not None
        assert len(sample_agent.matching_engine.features) > 0
    
    def test_analyze_and_recommend(self, sample_agent):
        """Test analyze_and_recommend functionality"""
        pain_point_data = {
            "pain_point": {
                "description": "We have trouble collecting customer feedback effectively",
                "context": {
                    "industry": "E-commerce",
                    "company_size": "medium",
                    "urgency_level": "high"
                },
                "affected_areas": ["customer_service"]
            }
        }
        
        result = sample_agent.analyze_and_recommend(pain_point_data)
        
        # Check analysis
        assert result.analysis is not None
        assert result.analysis.pain_point_summary is not None
        assert len(result.analysis.key_challenges) > 0
        assert result.analysis.impact_assessment is not None
        
        # Check solutions
        assert result.recommended_solutions is not None
        
        # Check next steps
        assert result.next_steps is not None
        assert len(result.next_steps.immediate_actions) > 0
    
    def test_list_available_features(self, sample_agent):
        """Test listing available features"""
        features = sample_agent.list_available_features()
        assert len(features) > 0
        assert features[0]["feature_name"] == "Test Feature"
    
    def test_get_feature_details(self, sample_agent):
        """Test getting feature details"""
        feature_detail = sample_agent.get_feature_details("test_feature")
        assert feature_detail is not None
        assert feature_detail["feature_name"] == "Test Feature"
        
        # Test non-existent feature
        non_existent = sample_agent.get_feature_details("non_existent")
        assert non_existent is None


class TestIntegration:
    """Integration tests for entire workflow"""
    
    def test_full_workflow_with_real_knowledge_base(self):
        """Test full workflow with real knowledge base"""
        # Use actual knowledge base file
        kb_path = Path(__file__).parent.parent / "data" / "knowledge_base.json"
        
        if not kb_path.exists():
            pytest.skip("Knowledge base file not found")
        
        agent = PainPointAgent(str(kb_path))
        
        # Test with real pain point
        pain_point = {
            "pain_point": {
                "description": "Difficulty collecting customer feedback, low response rate",
                "context": {
                    "industry": "E-commerce",
                    "company_size": "medium",
                    "urgency_level": "high"
                },
                "affected_areas": ["customer_service", "marketing"]
            }
        }
        
        result = agent.analyze_and_recommend(pain_point)
        
        # Verify results
        assert result.analysis.pain_point_summary is not None
        assert len(result.recommended_solutions) > 0
        assert all(sol.relevance_score > 0 for sol in result.recommended_solutions)
        
        # Test export
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            agent.export_analysis_report(result, f.name, format="json")
            
            # Verify file was created
            assert Path(f.name).exists()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
