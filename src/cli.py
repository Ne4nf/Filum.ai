"""
Command Line Interface for Pain Point to Solution Agent
"""

import typer
import json
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text

from agent import PainPointAgent
from models import PainPointInput
from utils import validate_pain_point_input

# Initialize Typer app and Rich console
app = typer.Typer(
    name="filum-agent",
    help="Filum.ai Pain Point to Solution Agent CLI",
    add_completion=False,
)
console = Console()


def print_header():
    """Print application header"""
    header_text = Text("🎯 Filum.ai Pain Point to Solution Agent", style="bold blue")
    console.print(Panel(header_text, expand=False))
    console.print()


@app.command()
def analyze(
    input_file: Optional[str] = typer.Option(
        None, "--input", "-i", help="Path to JSON file containing pain point input"
    ),
    output_file: Optional[str] = typer.Option(
        None, "--output", "-o", help="Output file path to save results"
    ),
    max_solutions: int = typer.Option(
        3, "--max-solutions", "-m", help="Maximum number of solutions to recommend"
    ),
    knowledge_base: Optional[str] = typer.Option(
        None, "--kb", help="Path to custom knowledge base file"
    ),
    interactive: bool = typer.Option(
        False, "--interactive", "-I", help="Interactive mode to input pain point"
    ),
):
    """Analyze pain point and recommend solutions"""
    print_header()

    try:
        # Initialize agent
        console.print("🔧 Initializing agent...", style="yellow")
        agent = PainPointAgent(knowledge_base)
        console.print("✅ Agent is ready!", style="green")
        console.print()

        # Get input
        if interactive:
            pain_point_data = get_interactive_input()
        elif input_file:
            pain_point_data = load_input_file(input_file)
        else:
            console.print(
                "❌ Need to provide --input file or use --interactive mode", style="red"
            )
            raise typer.Exit(1)

        # Validate input
        validation_errors = validate_pain_point_input(pain_point_data)
        if validation_errors:
            console.print("❌ Input validation errors:", style="red")
            for error in validation_errors:
                console.print(f"  - {error}", style="red")
            raise typer.Exit(1)

        # Analyze
        console.print("🔍 Analyzing pain point...", style="yellow")
        result = agent.analyze_and_recommend(pain_point_data, max_solutions)

        # Display results
        display_analysis_results(result)

        # Save output if requested
        if output_file:
            save_output_file(result, output_file)

        # Ask for demo requests
        if result.recommended_solutions:
            console.print()
            if Confirm.ask("💡 Would you like to request a demo for any solution?"):
                handle_demo_requests(result.recommended_solutions)

    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def list_features():
    """List all available features in knowledge base"""
    print_header()

    try:
        agent = PainPointAgent()
        features = agent.list_available_features()

        if not features:
            console.print("❌ No features found in knowledge base", style="red")
            return

        table = Table(title="📋 Available Filum.ai Features")
        table.add_column("Feature ID", style="cyan")
        table.add_column("Feature Name", style="green")
        table.add_column("Category", style="blue")
        table.add_column("Description", style="white")

        for feature in features:
            table.add_row(
                feature["feature_id"],
                feature["feature_name"],
                feature["category"],
                (
                    feature["description"][:60] + "..."
                    if len(feature["description"]) > 60
                    else feature["description"]
                ),
            )

        console.print(table)

    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def feature_detail(feature_id: str):
    """View detailed information about a specific feature"""
    print_header()

    try:
        agent = PainPointAgent()
        feature_detail = agent.get_feature_details(feature_id)

        if not feature_detail:
            console.print(f"❌ Feature not found with ID: {feature_id}", style="red")
            return

        # Display feature details
        console.print(
            f"🔍 Feature Details: {feature_detail['feature_name']}", style="bold blue"
        )
        console.print()

        console.print(f"📁 Category: {feature_detail['category']}", style="green")
        console.print(f"📂 Subcategory: {feature_detail['subcategory']}", style="green")
        console.print()

        console.print("📝 Description:", style="bold")
        console.print(f"  {feature_detail['description']['detailed']}")
        console.print()

        if feature_detail.get("capabilities"):
            console.print("⚡ Capabilities:", style="bold")
            for cap in feature_detail["capabilities"]:
                console.print(f"  • {cap['capability_name']}: {cap['description']}")
            console.print()

        if feature_detail.get("benefits", {}).get("quantitative"):
            console.print("📊 Quantitative Benefits:", style="bold")
            for benefit in feature_detail["benefits"]["quantitative"]:
                console.print(f"  • {benefit}")
            console.print()

        console.print(
            f"🔧 Complexity: {feature_detail['implementation']['complexity']}",
            style="yellow",
        )
        console.print(
            f"⏱️ Setup Time: {feature_detail['implementation']['setup_time']}",
            style="yellow",
        )

    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def demo():
    """Run demo with pain point samples"""
    print_header()

    # Sample pain points
    samples = [
        {
            "name": "E-commerce Feedback Collection",
            "data": {
                "pain_point": {
                    "description": "We have difficulty collecting customer feedback after they purchase. Currently only about 5% of customers respond to email surveys.",
                    "context": {
                        "industry": "E-commerce",
                        "company_size": "medium",
                        "urgency_level": "high",
                    },
                    "affected_areas": ["customer_service", "marketing"],
                }
            },
        },
        {
            "name": "Support Agent Overload",
            "data": {
                "pain_point": {
                    "description": "Support agents are overwhelmed by repetitive questions, response time has slowed to an average of 4 hours.",
                    "context": {
                        "industry": "SaaS",
                        "company_size": "large",
                        "urgency_level": "high",
                    },
                    "affected_areas": ["customer_service"],
                }
            },
        },
    ]

    console.print("🎮 Demo Mode - Choose pain point sample:", style="bold blue")
    console.print()

    for i, sample in enumerate(samples, 1):
        console.print(f"{i}. {sample['name']}")

    choice = Prompt.ask(
        "Choose sample number",
        choices=[str(i) for i in range(1, len(samples) + 1)],
        default="1",
    )

    selected_sample = samples[int(choice) - 1]

    console.print()
    console.print(f"🎯 Analyzing: {selected_sample['name']}", style="green")
    console.print()

    try:
        agent = PainPointAgent()
        result = agent.analyze_and_recommend(selected_sample["data"])
        display_analysis_results(result)

    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        raise typer.Exit(1)


def get_interactive_input() -> dict:
    """Get input from user in interactive mode"""
    console.print(
        "📝 Interactive Mode - Enter pain point information:", style="bold blue"
    )
    console.print()

    # Pain point description
    description = Prompt.ask("Describe your pain point in detail")

    # Industry
    industry = Prompt.ask("Industry (optional)", default="")

    # Company size
    company_size = Prompt.ask(
        "Company size",
        choices=["startup", "small", "medium", "large", "enterprise"],
        default="medium",
    )

    # Urgency level
    urgency_level = Prompt.ask(
        "Urgency level", choices=["low", "medium", "high"], default="medium"
    )

    # Affected areas
    console.print("Affected areas (can select multiple, separated by commas):")
    console.print("  - customer_service")
    console.print("  - marketing")
    console.print("  - sales")
    console.print("  - operations")

    affected_areas_input = Prompt.ask("Affected areas", default="customer_service")
    affected_areas = [area.strip() for area in affected_areas_input.split(",")]

    return {
        "pain_point": {
            "description": description,
            "context": {
                "industry": industry if industry else None,
                "company_size": company_size,
                "urgency_level": urgency_level,
            },
            "affected_areas": affected_areas,
        }
    }


def load_input_file(file_path: str) -> dict:
    """Load input from JSON file"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        console.print(f"❌ File does not exist: {file_path}", style="red")
        raise typer.Exit(1)
    except json.JSONDecodeError as e:
        console.print(f"❌ Invalid JSON file: {e}", style="red")
        raise typer.Exit(1)


def save_output_file(result, file_path: str):
    """Save results to file"""
    try:
        output_path = Path(file_path)

        if output_path.suffix.lower() == ".json":
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result.dict(), f, ensure_ascii=False, indent=2)
        elif output_path.suffix.lower() == ".md":
            # Export as markdown
            agent = PainPointAgent()
            agent._export_markdown_report(result, str(output_path))
        else:
            console.print(
                "❌ Only .json and .md output formats are supported", style="red"
            )
            return

        console.print(f"💾 Results saved to: {output_path}", style="green")

    except Exception as e:
        console.print(f"❌ Error saving file: {e}", style="red")


def display_analysis_results(result):
    """Display analysis results with Rich formatting"""
    console.print("📊 ANALYSIS RESULTS", style="bold blue")
    console.print("=" * 50, style="blue")
    console.print()

    # Analysis section
    console.print("🔍 PAIN POINT ANALYSIS", style="bold green")
    console.print(Panel(result.analysis.pain_point_summary, title="Summary"))
    console.print(Panel(result.analysis.impact_assessment, title="Impact Assessment"))

    if result.analysis.key_challenges:
        console.print("\n🎯 Key Challenges:", style="bold")
        for challenge in result.analysis.key_challenges:
            console.print(f"  • {challenge}")

    console.print()

    # Solutions section
    if result.recommended_solutions:
        console.print("💡 RECOMMENDED SOLUTIONS", style="bold green")
        console.print()

        for i, solution in enumerate(result.recommended_solutions, 1):
            console.print(
                f"🚀 Solution {i}: {solution.solution_name}", style="bold cyan"
            )
            console.print(f"   📊 Relevance Score: {solution.relevance_score}/1.0")
            console.print(f"   🔧 Complexity: {solution.complexity_level.value}")
            console.print(f"   ⏱️ Setup Time: {solution.estimated_setup_time}")
            console.print()
            console.print(f"   💬 How it helps: {solution.how_it_helps}")
            console.print()

            if solution.implementation_steps:
                console.print("   📋 Implementation Steps:")
                for j, step in enumerate(solution.implementation_steps, 1):
                    console.print(f"      {j}. {step}")
                console.print()

            if solution.expected_outcomes and solution.expected_outcomes.short_term:
                console.print("   🎯 Expected Short-term Outcomes:")
                for outcome in solution.expected_outcomes.short_term:
                    console.print(f"      • {outcome}")
                console.print()

            console.print("-" * 50)
            console.print()

    # Next steps
    if result.next_steps and result.next_steps.immediate_actions:
        console.print("📝 NEXT STEPS", style="bold green")
        for action in result.next_steps.immediate_actions:
            console.print(f"  • {action}")
        console.print()


def handle_demo_requests(solutions):
    """Handle demo requests from user"""
    console.print("🎬 Demo Requests:", style="bold blue")

    for i, solution in enumerate(solutions, 1):
        request_demo = Confirm.ask(f"Request demo for {solution.solution_name}?")
        if request_demo:
            console.print(
                f"✅ Demo request recorded for {solution.solution_name}", style="green"
            )
            # Here you can implement actual request logic

    console.print()
    console.print("📧 To book an actual demo, please contact:", style="yellow")
    console.print("   Email: demo@filum.ai")
    console.print("   Website: https://filum.ai/demo")


def main():
    """Entry point for CLI"""
    app()


if __name__ == "__main__":
    main()
