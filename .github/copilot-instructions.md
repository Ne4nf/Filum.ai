<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Filum.ai Pain Point to Solution Agent - Copilot Instructions

## Project Context
This is a Python project for building an AI agent that analyzes customer pain points and recommends solutions from the Filum.ai platform. The agent focuses on Customer Experience and Customer Service domains.

## Code Style Guidelines
- Use Vietnamese comments for business logic explanations
- Use English for technical comments and docstrings
- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Prefer descriptive variable names in English

## Architecture Patterns
- Use dependency injection for the knowledge base
- Implement strategy pattern for different matching algorithms
- Follow repository pattern for data access
- Use factory pattern for creating different types of solutions

## Key Components
1. **PainPointAgent**: Main agent class that orchestrates the analysis
2. **MatchingEngine**: Core algorithm for finding relevant solutions
3. **KnowledgeBase**: Repository of Filum.ai features and capabilities
4. **Models**: Pydantic models for input/output validation
5. **Utils**: Helper functions for text processing and scoring

## Business Domain Knowledge
- Focus on Customer Experience (CX) and Customer Service use cases
- Understand Filum.ai product categories: VoC, AI Customer Service, Insights, Customer 360, AI & Automation
- Consider business context: industry, company size, urgency level
- Prioritize actionable and measurable solutions

## Testing Guidelines
- Write unit tests for all core functions
- Include integration tests for the full workflow
- Use pytest fixtures for test data
- Mock external dependencies
- Test edge cases and error conditions

## Documentation Standards
- Use Vietnamese for user-facing documentation
- Use English for technical API documentation
- Include code examples in docstrings
- Maintain up-to-date README with setup instructions
