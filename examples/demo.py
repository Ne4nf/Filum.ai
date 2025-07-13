"""
Demo script for Pain Point to Solution Agent
Example usage of agent with real-world pain points
"""

import json
import sys
from pathlib import Path

# Add src to path to import modules
sys.path.append(str(Path(__file__).parent.parent / "src"))

from agent import PainPointAgent
from models import PainPointInput

def main():
    print("🎯 FILUM.AI PAIN POINT TO SOLUTION AGENT DEMO")
    print("=" * 60)
    print()
    
    # Sample pain points
    pain_points = [
        {
            "name": "E-commerce: Difficult feedback collection",
            "data": {
                "pain_point": {
                    "description": "We have difficulty collecting customer feedback after they make purchases. Currently only about 5% of customers respond to email surveys.",
                    "context": {
                        "industry": "E-commerce",
                        "company_size": "medium",
                        "current_tools": ["Email marketing platform", "Basic CRM"],
                        "urgency_level": "high"
                    },
                    "affected_areas": ["customer_service", "marketing"],
                    "current_impact": {
                        "description": "Lack of insights about customer experience, difficult to improve products and services",
                        "metrics": {
                            "customer_satisfaction": "Unknown",
                            "response_rate": "5%",
                            "churn_rate": "15%"
                        }
                    }
                },
                "preferences": {
                    "budget_range": "medium",
                    "implementation_timeline": "3_months",
                    "technical_complexity": "medium"
                }
            }
        },
        {
            "name": "SaaS: Support agents overloaded",
            "data": {
                "pain_point": {
                    "description": "Support agents are overwhelmed by repetitive questions. Current average response time is 4 hours, customers are not satisfied.",
                    "context": {
                        "industry": "SaaS",
                        "company_size": "small",
                        "current_tools": ["Zendesk", "Email support", "Phone support"],
                        "urgency_level": "critical"
                    },
                    "affected_areas": ["customer_service"],
                    "current_impact": {
                        "description": "Customer satisfaction decreases, agent burnout increases",
                        "metrics": {
                            "response_time": "4 hours",
                            "customer_satisfaction": "3.2/5",
                            "agent_utilization": "120%"
                        }
                    }
                },
                "preferences": {
                    "budget_range": "low",
                    "implementation_timeline": "1_month",
                    "technical_complexity": "low"
                }
            }
        },
        {
            "name": "Banking: Slow customer support response time",
            "data": {
                "pain_point": {
                    "description": "Customers complain about slow response times from the support team. On average, they wait 15-20 minutes via live chat, and email replies take 2-3 days.",
                    "context": {
                        "industry": "Banking",
                        "company_size": "large",
                        "current_tools": ["Legacy CRM", "Phone system", "Email"],
                        "urgency_level": "high"
                    },
                    "affected_areas": ["customer_service"],
                    "current_impact": {
                        "description": "Customer complaints increase, potential customer loss to competitors",
                        "metrics": {
                            "live_chat_wait_time": "15-20 minutes",
                            "email_response_time": "2-3 days",
                            "complaint_rate": "25%"
                        }
                    }
                },
                "preferences": {
                    "budget_range": "high",
                    "implementation_timeline": "6_months",
                    "technical_complexity": "high"
                }
            }
        },
        {
            "name": "Retail: Don\'t understand customer behavior",
            "data": {
                "pain_point": {
                    "description": "We have sales data but don\'t understand why customers buy this product and not others. We lack insights to improve products.",
                    "context": {
                        "industry": "Retail",
                        "company_size": "medium",
                        "current_tools": ["Google Analytics", "POS system"],
                        "urgency_level": "medium"
                    },
                    "affected_areas": ["product_development", "marketing"],
                    "current_impact": {
                        "description": "Cannot optimize product mix, ineffective marketing campaigns",
                        "metrics": {
                            "conversion_rate": "2.5%",
                            "return_rate": "12%",
                            "marketing_roi": "1.8x"
                        }
                    }
                },
                "preferences": {
                    "budget_range": "medium",
                    "implementation_timeline": "4_months",
                    "technical_complexity": "medium"
                }
            }
        },
        {
            "name": "Healthcare: Ineffective feedback collection",
            "data": {
                "pain_point": {
                    "description": "The hospital needs to collect patient satisfaction but the current process is very manual and doesn\'t capture complete insights.",
                    "context": {
                        "industry": "Healthcare",
                        "company_size": "large",
                        "current_tools": ["Paper surveys", "Basic database"],
                        "urgency_level": "medium"
                    },
                    "affected_areas": ["quality_management", "patient_experience"],
                    "current_impact": {
                        "description": "Cannot track service quality, difficult to improve patient experience",
                        "metrics": {
                            "survey_completion_rate": "30%",
                            "data_accuracy": "60%",
                            "processing_time": "1 week"
                        }
                    }
                },
                "preferences": {
                    "budget_range": "high",
                    "implementation_timeline": "6_months",
                    "technical_complexity": "medium"
                }
            }
        }
    ]
    
    # Initialize agent
    kb_path = Path(__file__).parent.parent / "data" / "knowledge_base.json"
    if not kb_path.exists():
        print("❌ Knowledge base file not found!")
        print(f"   Expected at: {kb_path}")
        return
    
    print("🤖 Initializing Pain Point Agent...")
    agent = PainPointAgent(str(kb_path))
    print("✅ Agent initialized successfully!\n")
    
    # Process each pain point
    for i, pain_point in enumerate(pain_points, 1):
        print(f"📝 Processing Pain Point {i}/{len(pain_points)}: {pain_point[\'name\']}")
        print("-" * 80)
        
        try:
            # Analyze pain point
            result = agent.analyze_and_recommend(pain_point["data"])
            
            # Display results
            print("📊 ANALYSIS RESULTS:")
            print(f"   Summary: {result.analysis.pain_point_summary}")
            print(f"   Impact: {result.analysis.impact_assessment}")
            print(f"   Key Challenges: {\', \'.join(result.analysis.key_challenges)}")
            
            print("\n💡 RECOMMENDED SOLUTIONS:")
            for i, solution in enumerate(result.recommended_solutions, 1):
                print(f"   {i}. {solution.solution_name}")
                print(f"      Relevance: {solution.relevance_score:.1%}")
                print(f"      Summary: {solution.solution_summary}")
                print(f"      Implementation: {solution.implementation_guide.complexity} complexity")
                print()
            
            print("🎯 NEXT STEPS:")
            print("   Immediate Actions:")
            for action in result.next_steps.immediate_actions:
                print(f"   • {action}")
            
            print("   Short-term Goals:")
            for goal in result.next_steps.short_term_goals:
                print(f"   • {goal}")
            
            # Export analysis
            export_path = f"analysis_results_{pain_point[\'name\'].lower().replace(\': \', \'_\').replace(\' \', \'_\')}.json"
            agent.export_analysis_report(result, export_path, format="json")
            print(f"\n📄 EXPORTED ANALYSIS TO: {export_path}")
            
        except Exception as e:
            print(f"❌ Error processing pain point: {e}")
        
        print("\n" + "=" * 80 + "\n")
    
    print("🎉 Demo completed!")
    print("\n📈 Summary:")
    print(f"   Processed {len(pain_points)} pain points")
    print("   All analysis results exported to JSON files")
    print("\n🔗 Next steps:")
    print("   1. Review the exported analysis files")
    print("   2. Contact Filum.ai team for implementation support")
    print("   3. Try the web interface: python web_demo.py")

if __name__ == "__main__":
    main()
