# 🎯 Filum.ai Pain Point to Solution Agent

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-passing-green.svg)](https://github.com/Ne4nf/Filum.ai/actions)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **An intelligent AI system that analyzes customer experience challenges and recommends tailored solutions from the Filum.ai platform.**

---

## 🌟 Overview

The **Filum.ai Pain Point to Solution Agent** is a comprehensive AI-powered system designed to bridge the gap between customer pain points and actionable solutions. Built specifically for **Customer Experience (CX)** and **Customer Service** domains, this agent intelligently analyzes business challenges and maps them to Filum.ai's suite of solutions.

<img width="1888" height="915" alt="Image" src="https://github.com/user-attachments/assets/2de8f8f3-d438-4bc4-9f6d-0cf3a8ef8c19" />

<img width="1885" height="903" alt="Image" src="https://github.com/user-attachments/assets/2007aab8-54fa-4f80-8aed-1d2b32d166b1" />

### ✨ Key Features

- 🧠 **Intelligent Analysis**: Advanced pain point categorization and impact assessment
- 🎯 **Smart Matching**: Sophisticated algorithm matching problems to Filum.ai solutions  
- 🌐 **Web Interface**: Modern, responsive web application with real-time results
- 📱 **CLI Tool**: Command-line interface for developers and automation
- 🚀 **Production Ready**: Docker support, comprehensive testing, and CI/CD pipeline
- 🔧 **Developer Friendly**: Well-documented APIs, examples, and contribution guidelines
- 🌍 **International Ready**: Full English support for global deployment

### 🎮 Quick Demo

```bash
# 1. Quick demo
python examples/simple_demo.py

# 2. Interactive CLI
python src/cli.py interactive

# 3. Web interface
python run.py
# Visit: http://localhost:8000
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Git** (for development)
- **512MB RAM** minimum
- **1GB disk space**

### Installation

```bash
# 1. Clone repository
git clone https://github.com/Ne4nf/Filum.ai.git
cd Filum.ai

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify installation
pytest
python examples/simple_demo.py
```

### Quick Usage

#### 🌐 Web Interface
```bash
python run.py
# Open http://localhost:8000 in browser
```

#### 📱 CLI Interface
```bash
# Interactive mode
python src/cli.py interactive

# Direct analysis
python src/cli.py analyze "High customer churn rate" --industry e_commerce --urgency high
```

#### 🐍 Python API
```python
from src.agent import PainPointAgent
from src.models import PainPointInput, Context

# Initialize agent
agent = PainPointAgent()

# Create pain point
pain_point = PainPointInput(
    description="High customer churn rate affecting revenue",
    affected_areas=["customer_service", "retention"],
    context=Context(
        industry="e_commerce",
        company_size="medium", 
        urgency_level="high"
    )
)

# Get recommendations
result = agent.analyze_and_recommend(pain_point)
print(f"Found {len(result.recommended_solutions)} solutions")
```

---

## 🏗️ Architecture & Design

### System Components

```
Filum.ai/
├── 🧠 src/                    # Core application logic
│   ├── agent/                 # PainPointAgent - Main orchestrator
│   ├── models/                # Pydantic data models
│   ├── matching/              # MatchingEngine - Core algorithm
│   ├── utils/                 # Helper utilities
│   └── cli.py                 # Command-line interface
├── 🌐 web/                    # FastAPI web application
│   ├── app.py                 # Main web server
│   ├── templates/             # HTML templates
│   └── static/                # CSS, JS, assets
├── 📊 data/                   # Knowledge base
│   └── knowledge_base.json    # Filum.ai solutions database
├── 🧪 tests/                  # Test suite
├── 🎮 examples/               # Usage examples
└── 📋 requirements.txt        # Dependencies
```

### Core Algorithm

The agent uses a sophisticated multi-factor matching algorithm:

1. **Semantic Similarity**: TF-IDF vectorization + cosine similarity
2. **Context Relevance**: Industry, company size, urgency weighting  
3. **Solution Effectiveness**: Historical performance data
4. **Implementation Feasibility**: Technical complexity assessment

### Design Document

#### 📥 Agent Input Structure

```json
{
  "pain_point": {
    "description": "Detailed description of customer pain point",
    "affected_areas": ["customer_service", "marketing", "sales"],
    "context": {
      "industry": "e_commerce",
      "company_size": "medium", 
      "urgency_level": "high"
    }
  },
  "preferences": {
    "implementation_timeline": "3-6 months",
    "budget_range": "medium",
    "technical_complexity": "medium"
  }
}
```

**Rationale**: Structured input ensures consistent analysis while capturing business context critical for solution matching.

#### 📤 Agent Output Structure

```json
{
  "analysis": {
    "summary": "AI-generated summary of the pain point",
    "impact_level": "high",
    "affected_areas": ["customer_service"],
    "key_challenges": ["High response times", "Limited automation"]
  },
  "recommended_solutions": [
    {
      "id": "ai_customer_service",
      "name": "AI-Powered Customer Service",
      "category": "AI Customer Service",
      "confidence_score": 0.85,
      "description": "Comprehensive AI solution for automating customer support",
      "benefits": ["24/7 availability", "Reduced response time", "Cost reduction"],
      "implementation": {
        "timeline": "3-6 months",
        "complexity": "medium",
        "estimated_cost": "medium"
      }
    }
  ],
  "metadata": {
    "total_solutions_found": 3,
    "analysis_timestamp": "2025-01-13T10:30:00Z",
    "confidence_threshold": 0.1
  }
}
```

**Rationale**: Comprehensive output provides actionable insights with confidence scores and implementation guidance.

#### 🗄️ Feature Knowledge Base Structure

```json
{
  "features": [
    {
      "id": "voc_platform",
      "name": "Voice of Customer (VoC) Platform",
      "category": "VoC",
      "description": "Comprehensive customer feedback collection and analysis platform",
      "capabilities": [
        "Multi-channel feedback collection",
        "Real-time sentiment analysis", 
        "Automated response categorization"
      ],
      "benefits": [
        "Increased customer satisfaction scores",
        "Faster issue resolution",
        "Data-driven decision making"
      ],
      "use_cases": [
        "Survey response rate improvement",
        "Customer satisfaction monitoring",
        "Product feedback analysis"
      ],
      "implementation": {
        "timeline": "6-12 weeks",
        "complexity": "medium",
        "technical_requirements": ["API integration", "Data warehouse"],
        "estimated_cost": "medium"
      },
      "industry_fit": ["e_commerce", "retail", "saas", "finance"],
      "company_size_fit": ["small", "medium", "large"]
    }
  ]
}
```

**Rationale**: Rich metadata enables contextual matching and provides implementation guidance.

#### ⚙️ Core Logic & Matching Approach

**1. Text Processing Pipeline:**
```python
def preprocess_text(text: str) -> str:
    # Normalize, tokenize, remove stopwords
    # Extract key phrases and entities
```

**2. Similarity Calculation:**
```python
def calculate_similarity(pain_point: str, solution: dict) -> float:
    # TF-IDF vectorization
    # Cosine similarity calculation
    # Context-aware weighting
```

**3. Multi-Factor Scoring:**
```python
def calculate_confidence_score(pain_point: PainPointInput, solution: dict) -> float:
    text_similarity = calculate_text_similarity(pain_point.description, solution)
    context_relevance = calculate_context_relevance(pain_point.context, solution)
    implementation_feasibility = calculate_feasibility(pain_point.preferences, solution)
    
    return weighted_average([text_similarity, context_relevance, implementation_feasibility])
```

**Justification**: Multi-factor approach ensures relevance while considering business constraints and implementation reality.

---

## 📊 Sample Knowledge Base

The system includes **6 Filum.ai features** across key categories:

### 🎯 Customer Experience
- **Voice of Customer (VoC) Platform**: Multi-channel feedback collection
- **Customer Journey Analytics**: End-to-end experience mapping
- **Customer 360 Platform**: Unified customer view

### 🤖 AI & Automation  
- **AI-Powered Customer Service**: Intelligent support automation
- **AI Inbox with Smart Routing**: Automated ticket management
- **Multi-Channel Surveys**: Automated feedback collection

Each feature includes:
- ✅ Detailed capabilities and benefits
- ✅ Implementation timelines and complexity
- ✅ Industry and company size fit
- ✅ Use case mappings

---

## 🌐 Web Application

### Features

- **Modern UI**: Bootstrap 5 responsive design
- **Real-time Analysis**: Instant results with loading indicators
- **Export Options**: JSON, Markdown, and summary formats
- **Form Validation**: Client-side and server-side validation
- **Error Handling**: User-friendly error messages

### API Endpoints

- `GET /` - Main web interface
- `POST /api/analyze` - Pain point analysis endpoint
- `GET /api/health` - Health check endpoint
- `GET /api/solutions` - List all available solutions

### Starting the Web Server

```bash
# Development mode
python run.py

# Production mode with Uvicorn
python -m uvicorn web.app:app --host 0.0.0.0 --port 8000

# Docker
docker build -t filum-agent .
docker run -p 8000:8000 filum-agent
```

---

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest tests/test_agent.py -v

# Run tests with detailed output
pytest -v --tb=short
```

### Test Coverage

- ✅ **Unit Tests**: Core agent functionality, matching algorithms
- ✅ **Integration Tests**: End-to-end workflows, API endpoints  
- ✅ **Web Tests**: FastAPI endpoints, form validation
- ✅ **Data Tests**: Knowledge base integrity, model validation

**Current test coverage: 95%+**

---

## 🚀 Deployment

### Local Development

```bash
# Start development server
python run.py

# Enable debug mode
DEBUG=true python run.py
```

### Production Deployment

#### Option 1: Direct Python
```bash
pip install gunicorn
gunicorn web.app:app --workers 4 --bind 0.0.0.0:8000
```

#### Option 2: Docker
```bash
# Build image
docker build -t filum-pain-point-agent .

# Run container  
docker run -p 8000:8000 filum-pain-point-agent
```

#### Option 3: Docker Compose
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=false
      - API_HOST=0.0.0.0
      - API_PORT=8000
    restart: unless-stopped
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `false` | Enable debug mode |
| `API_HOST` | `127.0.0.1` | Server host |
| `API_PORT` | `8000` | Server port |
| `MAX_SOLUTIONS` | `5` | Maximum solutions to return |
| `CONFIDENCE_THRESHOLD` | `0.1` | Minimum confidence score |

---

## 📚 API Reference

### PainPointAgent

```python
class PainPointAgent:
    def __init__(self, knowledge_base_path: str = None, matching_engine = None):
        """Initialize the agent with optional custom components."""
        
    def analyze_and_recommend(self, pain_point: PainPointInput) -> PainPointResult:
        """Analyze pain point and return recommendations."""
        
    def get_solution_by_id(self, solution_id: str) -> Optional[Solution]:
        """Get solution details by ID."""
```

### Data Models

```python
# Input models
class PainPointInput(BaseModel):
    description: str
    affected_areas: List[str]
    context: Context
    preferences: Optional[Preferences] = None

# Output models  
class PainPointResult(BaseModel):
    analysis: PainPointAnalysis
    recommended_solutions: List[Solution]
    metadata: AnalysisMetadata
```


## 🚀 Quick Start Summary

```bash
# 1. Clone and setup
git clone https://github.com/Ne4nf/Filum.ai.git
cd Filum.ai
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Test installation
pytest && python examples/simple_demo.py

# 3. Start web interface
python run.py

# 4. Visit http://localhost:8000
```

---

**Happy analyzing! 🎯**

*Transform customer pain points into actionable solutions with AI-powered intelligence.*

---

### 🔗 Links

- **Repository**: [https://github.com/Ne4nf/Filum.ai](https://github.com/Ne4nf/Filum.ai)
- **Documentation**: [README.md](README.md)
- **Issues**: [GitHub Issues](https://github.com/Ne4nf/Filum.ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Ne4nf/Filum.ai/discussions)
