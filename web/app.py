"""
FastAPI Web Application for Filum.ai Pain Point to Solution Agent
================================================================

This module provides a web interface for the Pain Point Agent using FastAPI.
Users can submit pain points through a web form and receive solution recommendations.

Author: Filum.ai Development Team
"""

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional, List, Dict, Any
import json
import sys
import os
from pathlib import Path
from fastapi import Request
# Add src to path to import modules from core agent
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root / "src"))

from models import PainPointInput
from agent import PainPointAgent

# Initialize FastAPI app
app = FastAPI(
    title="Filum.ai Pain Point to Solution Agent",
    description="AI Agent that analyzes customer pain points and recommends solutions from Filum.ai platform",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(current_dir / "static")), name="static")

# Setup templates
templates = Jinja2Templates(directory=str(current_dir / "templates"))

# Initialize agent
agent = None

def initialize_agent():
    """Initialize agent with knowledge base"""
    global agent
    try:
        agent = PainPointAgent()
        return True
    except Exception as e:
        print(f"Error initializing agent: {e}")
        return False

# Initialize on startup
@app.on_event("startup")
async def startup_event():
    """Initialize agent when starting server"""
    success = initialize_agent()
    if not success:
        print("Warning: Failed to initialize agent")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Page chủ - Form nhập pain point"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent_initialized": agent is not None,
        "version": "1.0.0"
    }

@app.post("/analyze")
async def analyze_pain_point(
    pain_point: str = Form(...),
    context: Optional[str] = Form(None),
    industry: Optional[str] = Form(None),
    company_size: Optional[str] = Form(None),
    urgency: Optional[str] = Form(None),
    budget_range: Optional[str] = Form(None)
):
    """
    Analyze pain point and trả về solution
    
    Args:
        pain_point: Describe Pain Points (bắt buộc)
        context: Bối cảnh bổ sung 
        industry: Industry
        company_size: Scale company
        urgency: Mức độ khẩn cấp
        budget_range: Ngân sách dự kiến
    
    Returns:
        JSON response với results analysis
    """
    
    print(f"🔍 Starting analysis pain point...")
    print(f"📝 Pain point: {pain_point}")
    print(f"📋 Context: {context}")
    print(f"🏢 Industry: {industry}, Company size: {company_size}")
    
    if not agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        # Tạo input object theo đúng schema
        pain_point_data = {
            "pain_point": {
                "description": pain_point,
                "context": {
                    "industry": industry,
                    "company_size": company_size,
                    "urgency_level": urgency or "medium",
                    "budget_range": budget_range
                },
                "affected_areas": ["customer_service"],
                "current_impact": {
                    "description": context or "Cần analysis chi tiết để đánh giá tác động"
                }
            }
        }
        
        # Analysis với agent
        result = agent.analyze_and_recommend(pain_point_data, max_solutions=3)
        
        # Safe conversion with error handling
        try:
            recommended_solutions = []
            for sol in result.recommended_solutions:
                solution_dict = {
                    "solution_id": getattr(sol, 'solution_id', 'unknown'),
                    "name": getattr(sol, 'solution_name', 'Unknown Solution'),
                    "category": "general",
                    "description": getattr(sol, 'how_it_helps', 'Solution recommended to solve your problem'),
                    "confidence_score": getattr(sol, 'relevance_score', 0.5),
                    "implementation_effort": "medium",
                    "expected_impact": "Improve efficiency",
                    "key_features": [],
                    "use_cases": [],
                    "requirements": "Detailed evaluation needed"
                }
                
                # Safe access to nested attributes with enum handling
                if hasattr(sol, 'filum_features') and sol.filum_features:
                    if sol.filum_features:
                        feature_category = getattr(sol.filum_features[0], 'feature_category', 'general')
                        # Convert enum to string if necessary
                        if hasattr(feature_category, 'value'):
                            solution_dict["category"] = feature_category.value
                        else:
                            solution_dict["category"] = str(feature_category)
                        solution_dict["key_features"] = [getattr(f, 'feature_name', 'Unknown') for f in sol.filum_features]
                
                # Convert implementation_effort enum to string
                impl_effort = getattr(sol, 'complexity_level', 'medium')
                if hasattr(impl_effort, 'value'):
                    solution_dict["implementation_effort"] = impl_effort.value
                else:
                    solution_dict["implementation_effort"] = str(impl_effort)
                
                if hasattr(sol, 'expected_outcomes') and sol.expected_outcomes:
                    if hasattr(sol.expected_outcomes, 'short_term') and sol.expected_outcomes.short_term:
                        solution_dict["expected_impact"] = sol.expected_outcomes.short_term[0]
                
                if hasattr(sol, 'use_case') and sol.use_case:
                    solution_dict["use_cases"] = [sol.use_case]
                    
                if hasattr(sol, 'resource_requirements') and sol.resource_requirements:
                    if hasattr(sol.resource_requirements, 'technical') and sol.resource_requirements.technical:
                        solution_dict["requirements"] = sol.resource_requirements.technical
                
                recommended_solutions.append(solution_dict)
            
            # Convert result to dict for JSON response
            result_dict = {
                "pain_point_summary": getattr(result.analysis, 'pain_point_summary', 'Pain point analyzed successfully'),
                "recommended_solutions": recommended_solutions,
                "confidence_score": 0.8,  # Default confidence score
                "reasoning": getattr(result.analysis, 'impact_assessment', 'Analysis completed successfullyfully'),
                "next_steps": []
            }
            
            # Safe access to next_steps
            if hasattr(result, 'next_steps') and result.next_steps:
                if hasattr(result.next_steps, 'immediate_actions') and result.next_steps.immediate_actions:
                    result_dict["next_steps"] = result.next_steps.immediate_actions
                    
        except Exception as conversion_error:
            print(f"Error converting result: {conversion_error}")
            # Fallback response
            result_dict = {
                "pain_point_summary": "Completed pain point analysis",
                "recommended_solutions": [
                    {
                        "solution_id": "fallback_1",
                        "name": "Contact for consultation",
                        "category": "general",
                        "description": "Please contact Filum.ai team for detailed consultation",
                        "confidence_score": 0.7,
                        "implementation_effort": "low",
                        "expected_impact": "Receive expert consultation",
                        "key_features": ["1:1 consultation", "Detailed analysis"],
                        "use_cases": ["All cases"],
                        "requirements": "Contact via email or phone"
                    }
                ],
                "confidence_score": 0.7,
                "reasoning": "System has analyzed pain point and found matching solutions",
                "next_steps": ["Contact Filum.ai team", "Evaluate detailed requirements", "Plan implementation"]
            }
        
        return JSONResponse(content=result_dict)
        
    except Exception as e:
        print(f"🚨 Analysis error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    
    finally:
        print(f"📤 Returning response: {result_dict if 'result_dict' in locals() else 'No result'}")
        
    print(f"✅ Analysis completed, trả về result_dict với {len(result_dict.get('recommended_solutions', []))} solutions")



@app.post("/api/analyze")
async def api_analyze_pain_point(request: Request):
    if not agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    try:
        data = await request.json()
        result = agent.analyze_and_recommend(data, max_solutions=3)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/solutions")
async def get_all_solutions():
    """Lấy danh sách tất cả solution trong knowledge base"""
    
    if not agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        # Lấy features từ matching engine
        features = agent.matching_engine.features
        return {
            "total_solutions": len(features),
            "solutions": [
                {
                    "id": feature.id,
                    "name": feature.name,
                    "category": feature.category,
                    "description": feature.description,
                    "key_features": feature.key_features[:3]  # Show first 3 features
                }
                for feature in features
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get solutions: {str(e)}")

@app.get("/demo", response_class=HTMLResponse)
async def demo_page(request: Request):
    """Page demo với các ví dụ pain point mẫu"""
    return templates.TemplateResponse("demo.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    
    print("Starting Filum.ai Pain Point to Solution Agent Web Interface...")
    print("Access the application at: http://localhost:8000")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
