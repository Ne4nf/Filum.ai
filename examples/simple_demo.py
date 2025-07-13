"""
Simple demo script for Pain Point Agent
Does not use relative imports for easy execution
"""

import json
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Import after adding path
from models import PainPointInput
from agent import PainPointAgent


def simple_demo():
    """Run a simple demo"""
    print("🎯 FILUM.AI PAIN POINT AGENT - SIMPLE DEMO")
    print("=" * 50)
    print()
    
    # Sample pain point
    pain_point_data = {
        "pain_point": {
            "description": "Customers don't respond to surveys, response rate is very low at only 5%",
            "context": {
                "industry": "E-commerce",
                "company_size": "medium",
                "urgency_level": "high"
            },
            "affected_areas": ["marketing", "customer_service"]
        }
    }
    
    print("📝 Pain Point:")
    print(f"   {pain_point_data['pain_point']['description']}")
    print()
    
    try:
        print("🔧 Initializing agent...")
        agent = PainPointAgent()
        print("✅ Agent is ready!")
        print()
        
        print("🔍 Analyzing...")
        result = agent.analyze_and_recommend(pain_point_data, max_solutions=2)
        
        print("📊 ANALYSIS RESULTS:")
        print(f"   Summary: {result.analysis.pain_point_summary}")
        print(f"   Impact: {result.analysis.impact_assessment}")
        print()
        
        print("💡 RECOMMENDED SOLUTIONS:")
        for i, solution in enumerate(result.recommended_solutions, 1):
            print(f"   {i}. {solution.solution_name}")
            print(f"      ⭐ Score: {solution.relevance_score}")
            print(f"      💬 How it helps: {solution.how_it_helps}")
            print()
        
        print("📝 NEXT STEPS:")
        for action in result.next_steps.immediate_actions:
            print(f"   • {action}")
        
        print()
        print("✅ Demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    simple_demo()
