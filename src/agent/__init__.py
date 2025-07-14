"""
Pain Point Agent - Main orchestrator class
Coordinates the entire workflow from input analysis to output generation
"""

from typing import List, Dict, Optional
import json
import os
import re
from pathlib import Path

from models import (
    PainPointInput,
    AgentOutput,
    PainPointAnalysis,
    AlternativeApproach,
    NextSteps,
    Solution,
)
from matching import MatchingEngine


class PainPointAgent:
    """
    Main agent class to analyze pain points and recommend solutions
    """

    def __init__(self, knowledge_base_path: Optional[str] = None):
        """
        Initialize Pain Point Agent

        Args:
            knowledge_base_path: Path to knowledge base file
        """
        # Use default knowledge base if not provided
        if knowledge_base_path is None:
            current_dir = Path(__file__).parent.parent.parent
            knowledge_base_path = current_dir / "data" / "knowledge_base.json"

        self.matching_engine = MatchingEngine(str(knowledge_base_path))

        # Cache for performance
        self._analysis_cache: Dict[str, PainPointAnalysis] = {}

    def analyze_and_recommend(
        self, pain_point_input: Dict | PainPointInput, max_solutions: int = 3
    ) -> AgentOutput:
        """
        Analyze pain point and recommend solutions

        Args:
            pain_point_input: Input data from user (dict or PainPointInput object)
            max_solutions: Maximum number of solutions

        Returns:
            AgentOutput with analysis and recommendations
        """
        # Validate and convert input
        if isinstance(pain_point_input, dict):
            pain_point = PainPointInput(**pain_point_input)
        else:
            pain_point = pain_point_input

        print("🔍 Starting pain point analysis...")

        # Step 1: Analyze pain point
        analysis = self._analyze_pain_point(pain_point)
        print("✅ Completed pain point analysis")

        # Step 2: Find matching solutions
        print("🎯 Searching for matching solutions...")
        solutions = self.matching_engine.find_matching_solutions(
            pain_point, max_solutions
        )
        print(f"✅ Found {len(solutions)} matching solutions")

        # Step 3: Generate alternative approaches
        alternatives = self._generate_alternatives(pain_point, solutions)

        # Step 4: Generate next steps
        next_steps = self._generate_next_steps(pain_point, solutions)

        return AgentOutput(
            analysis=analysis,
            recommended_solutions=solutions,
            alternative_approaches=alternatives,
            next_steps=next_steps,
        )

    def _analyze_pain_point(self, pain_point: PainPointInput) -> PainPointAnalysis:
        """
        Analysis and summarize pain point

        Args:
            pain_point: Input pain point

        Returns:
            PainPointAnalysis object
        """
        description = pain_point.pain_point.description
        context = pain_point.pain_point.context
        affected_areas = pain_point.pain_point.affected_areas
        current_impact = pain_point.pain_point.current_impact

        # Generate summary
        summary_parts = [f"Main issue: {description}"]

        if context and context.industry:
            summary_parts.append(f"Industry: {context.industry}")

        if context and context.company_size:
            summary_parts.append(f"Scale: {context.company_size.value}")

        if affected_areas:
            summary_parts.append(f"Affected areas: {', '.join(affected_areas)}")

        summary = ". ".join(summary_parts)

        # Identify key challenges
        challenges = self._extract_key_challenges(pain_point)

        # Assess impact
        impact_assessment = self._assess_impact(pain_point)

        return PainPointAnalysis(
            pain_point_summary=summary,
            key_challenges=challenges,
            impact_assessment=impact_assessment,
        )

    def _extract_key_challenges(self, pain_point: PainPointInput) -> List[str]:
        """Extract key challenges from pain point description"""
        description = pain_point.pain_point.description.lower()

        # Challenge patterns and corresponding challenges
        challenge_patterns = {
            r"difficulty|struggle|hard|challenging": "Difficulty implementing current processes",
            r"no idea|unclear|lack of visibility|unknown": "Lack of visibility and necessary information",
            r"overload|overwhelm|too much|burden": "Work and resource overload",
            r"slow|delay|late|sluggish": "Slow processing and response times",
            r"manual|time-consuming|labor intensive": "Time-consuming manual processes",
            r"inconsistent|variation|different": "Lack of consistency in processes",
            r"low rate|poor performance|inefficient": "Low performance and success rates",
        }

        challenges = []
        import re

        for pattern, challenge in challenge_patterns.items():
            if re.search(pattern, description):
                challenges.append(challenge)

        # Add context-based challenges
        if pain_point.pain_point.affected_areas:
            if "customer_service" in pain_point.pain_point.affected_areas:
                challenges.append("Need to improve customer service quality")
            if "marketing" in pain_point.pain_point.affected_areas:
                challenges.append("Need to optimize marketing effectiveness")

        # Ensure we have at least some challenges
        if not challenges:
            challenges = [
                "Need to improve efficiency of current processes",
                "Lack of automation and intelligence in workflow",
            ]

        return challenges[:4]  # Limit to 4 challenges

    def _assess_impact(self, pain_point: PainPointInput) -> str:
        """Assess the impact level of the pain point"""
        context = pain_point.pain_point.context
        current_impact = pain_point.pain_point.current_impact

        impact_factors = []

        # Assess urgency
        if context and context.urgency_level:
            urgency = context.urgency_level.value
            urgency_map = {
                "high": "Serious impact, needs immediate resolution",
                "medium": "Significant impact, needs to be addressed soon",
                "low": "Limited impact, can be planned for long-term",
            }
            impact_factors.append(
                urgency_map.get(urgency, "Impact level needs further assessment")
            )

        # Assess based on affected areas
        affected_areas = pain_point.pain_point.affected_areas
        if len(affected_areas) > 2:
            impact_factors.append("Multi-area impact, needs comprehensive solution")
        elif "customer_service" in affected_areas:
            impact_factors.append("Directly affects customer experience")

        # Assess based on current metrics
        if current_impact and current_impact.metrics:
            metrics = current_impact.metrics
            if (
                metrics.customer_satisfaction
                and "low" in str(metrics.customer_satisfaction).lower()
            ):
                impact_factors.append(
                    "Customer satisfaction is being negatively affected"
                )
            if metrics.response_time and any(
                word in str(metrics.response_time).lower() for word in ["slow", "high"]
            ):
                impact_factors.append(
                    "Current response time does not meet requirements"
                )

        # Company size impact
        if context and context.company_size:
            size = context.company_size.value
            if size in ["large", "enterprise"]:
                impact_factors.append(
                    "At large scale, impact may affect many customers"
                )

        if not impact_factors:
            return "This issue is affecting operational efficiency and needs to be resolved"

        return ". ".join(impact_factors)

    def _generate_alternatives(
        self, pain_point: PainPointInput, solutions: List[Solution]
    ) -> List[AlternativeApproach]:
        """Generate alternative approaches besides Filum.ai solutions"""
        alternatives = []

        description = pain_point.pain_point.description.lower()

        # Alternative 1: Internal process improvement
        if any(word in description for word in ["manual", "process"]):
            alternatives.append(
                AlternativeApproach(
                    approach_name="Improve Internal Processes",
                    description="Optimize current processes through training and process redesign",
                    pros_cons={
                        "pros": [
                            "Lower cost",
                            "Use existing resources",
                            "Full control over processes",
                        ],
                        "cons": [
                            "Takes long time to see results",
                            "Depends on team discipline",
                            "Difficult to scale as business grows",
                        ],
                    },
                )
            )

        # Alternative 2: Third-party tools
        if len(solutions) > 0:
            alternatives.append(
                AlternativeApproach(
                    approach_name="Use Third-Party Tools",
                    description="Integrate specialized tools from different vendors",
                    pros_cons={
                        "pros": [
                            "Many options available in market",
                            "Can find specialized tools",
                            "Flexible to change",
                        ],
                        "cons": [
                            "Difficult integration between tools",
                            "Data silos and fragmentation",
                            "High integration costs",
                        ],
                    },
                )
            )

        # Alternative 3: Build in-house
        if pain_point.pain_point.context and pain_point.pain_point.context.company_size:
            size = pain_point.pain_point.context.company_size.value
            if size in ["large", "enterprise"]:
                alternatives.append(
                    AlternativeApproach(
                        approach_name="Develop In-House Solution",
                        description="Build custom system with internal development team",
                        pros_cons={
                            "pros": [
                                "Complete customization",
                                "Full ownership of source code",
                                "Can adapt to business changes",
                            ],
                            "cons": [
                                "High development cost and time",
                                "Need specialized technical team",
                                "Long-term maintenance and support",
                            ],
                        },
                    )
                )

        return alternatives[:2]  # Limit to 2 alternatives

    def _generate_next_steps(
        self, pain_point: PainPointInput, solutions: List[Solution]
    ) -> NextSteps:
        """Generate next steps for user"""
        immediate_actions = [
            "Detailed evaluation of recommended solutions",
            "Determine budget and timeline for project",
            "Identify key stakeholders to participate in decision making",
        ]

        # Add specific actions based on context
        if pain_point.pain_point.context:
            context = pain_point.pain_point.context

            if context.urgency_level and context.urgency_level.value == "high":
                immediate_actions.insert(
                    0, "Organize urgent meeting with leadership team"
                )

            if not context.current_tools:
                immediate_actions.append("Audit current tools and systems")

        # Add solution-specific actions
        if solutions:
            top_solution = solutions[0]
            immediate_actions.append(
                f"Learn more about {top_solution.solution_name} (relevance score: {top_solution.relevance_score})"
            )

        # Determine if consultation needed
        consultation_needed = True
        if solutions and len(solutions) > 0:
            avg_complexity = sum(
                (
                    1
                    if sol.complexity_level.value == "low"
                    else 2 if sol.complexity_level.value == "medium" else 3
                )
                for sol in solutions
            ) / len(solutions)
            consultation_needed = avg_complexity > 1.5

        # Generate demo requests
        demo_requests = []
        for solution in solutions[:2]:  # Top 2 solutions
            demo_requests.append(f"Demo {solution.solution_name}")

        return NextSteps(
            immediate_actions=immediate_actions[:4],  # Limit to 4 actions
            consultation_needed=consultation_needed,
            demo_requests=demo_requests,
        )

    def get_feature_details(self, feature_id: str) -> Optional[Dict]:
        """
        Get details about a specific feature

        Args:
            feature_id: ID of the feature

        Returns:
            Dictionary chứa thông tin chi tiết feature
        """
        if not self.matching_engine.features:
            return None

        for feature in self.matching_engine.features:
            if feature.feature_id == feature_id:
                return feature.dict()

        return None

    def list_available_features(self) -> List[Dict[str, str]]:
        """
        List all features available in knowledge base

        Returns:
            List of dictionaries with basic feature information
        """
        if not self.matching_engine.features:
            return []

        return [
            {
                "feature_id": feature.feature_id,
                "feature_name": feature.feature_name,
                "category": feature.category.value,
                "description": feature.description.short,
            }
            for feature in self.matching_engine.features
        ]

    def export_analysis_report(
        self, output: AgentOutput, file_path: str, format: str = "json"
    ) -> None:
        """
        Export results analysis ra file

        Args:
            output: AgentOutput from analyze_and_recommend
            file_path: Đường dẫn file output
            format: Định dạng file ("json" hoặc "markdown")
        """
        if format.lower() == "json":
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(output.dict(), f, ensure_ascii=False, indent=2)
        elif format.lower() == "markdown":
            self._export_markdown_report(output, file_path)
        else:
            raise ValueError(
                "Format not supported. Only 'json' and 'markdown' are supported"
            )

        print(f"✅ Đã export report ra {file_path}")

    def _export_markdown_report(self, output: AgentOutput, file_path: str) -> None:
        """Export report as Markdown"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("# Pain Point Analysis Report\n\n")

            # Analysis section
            f.write("## Pain Point Analysis\n\n")
            f.write(f"**Summary:** {output.analysis.pain_point_summary}\n\n")
            f.write(f"**Impact Assessment:** {output.analysis.impact_assessment}\n\n")

            f.write("**Key Challenges:**\n")
            for challenge in output.analysis.key_challenges:
                f.write(f"- {challenge}\n")
            f.write("\n")

            # Solutions section
            f.write("## Recommended Solutions\n\n")
            for i, solution in enumerate(output.recommended_solutions, 1):
                f.write(f"### {i}. {solution.solution_name}\n\n")
                f.write(f"**Matching Score:** {solution.relevance_score}/1.0\n\n")
                f.write(f"**How it helps:** {solution.how_it_helps}\n\n")

                f.write("**Implementation Steps:**\n")
                for step in solution.implementation_steps:
                    f.write(f"1. {step}\n")
                f.write("\n")

                if solution.expected_outcomes.short_term:
                    f.write("**Short-term Results:**\n")
                    for outcome in solution.expected_outcomes.short_term:
                        f.write(f"- {outcome}\n")
                    f.write("\n")

            # Next steps
            if output.next_steps:
                f.write("## Next Steps\n\n")
                for action in output.next_steps.immediate_actions:
                    f.write(f"- {action}\n")
                f.write("\n")

        print(f"✅ Markdown report generated: {file_path}")
