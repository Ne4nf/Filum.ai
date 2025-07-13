"""
Launcher script for Filum.ai Pain Point Agent
Solves import issues and provides easy-to-use entry points
"""

import sys
from pathlib import Path

# Add src to path to import modules
current_dir = Path(__file__).parent
src_path = current_dir / "src"
sys.path.insert(0, str(src_path))


def run_demo():
    """Run demo script"""
    from examples.simple_demo import simple_demo
    simple_demo()


def run_cli():
    """Run CLI interface"""
    from cli import main
    main()


def run_web_server(host="127.0.0.1", port=8000, reload=False):
    """Run web server interface"""
    import subprocess
    import sys
    
    cmd = [
        sys.executable, 
        "web/server.py", 
        "--host", host, 
        "--port", str(port)
    ]
    
    if reload:
        cmd.append("--reload")
    
    print(f"🚀 Starting web server at http://{host}:{port}")
    print("Press Ctrl+C to stop the server")
    
    try:
        subprocess.run(cmd, cwd=current_dir)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")


def run_analysis(input_file=None, interactive=False):
    """Run analysis with options"""
    from agent import PainPointAgent
    
    if interactive:
        # Simple interactive mode
        description = input("Enter pain point description: ")
        industry = input("Industry (optional): ") or None
        company_size = input("Company size [startup/small/medium/large/enterprise]: ") or "medium"
        
        pain_point = {
            "pain_point": {
                "description": description,
                "context": {
                    "industry": industry,
                    "company_size": company_size,
                    "urgency_level": "medium"
                },
                "affected_areas": ["customer_service"]
            }
        }
    elif input_file:
        import json
        with open(input_file, 'r', encoding='utf-8') as f:
            pain_point = json.load(f)
    else:
        print("Need to provide input_file or use interactive=True")
        return
    
    # Run analysis
    agent = PainPointAgent()
    result = agent.analyze_and_recommend(pain_point)
    
    # Display results
    print(f"\n📊 Analysis Results:")
    print(f"Summary: {result.analysis.pain_point_summary}")
    print(f"\n💡 Top Solutions:")
    for i, sol in enumerate(result.recommended_solutions[:2], 1):
        print(f"{i}. {sol.solution_name} (Score: {sol.relevance_score})")
        print(f"   {sol.how_it_helps}")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("🎯 Filum.ai Pain Point Agent")
        print("\nUsage:")
        print("  python run.py demo              - Run demo")
        print("  python run.py cli               - Run CLI interface")
        print("  python run.py web               - Run web server (localhost:8000)")
        print("  python run.py web --host HOST --port PORT --reload")
        print("  python run.py analyze           - Interactive analysis")
        print("  python run.py file <path>       - Analyze from file")
        
    elif sys.argv[1] == "demo":
        run_demo()
    elif sys.argv[1] == "cli":
        run_cli()
    elif sys.argv[1] == "web":
        # Parse web server arguments
        host = "127.0.0.1"
        port = 8000
        reload = False
        
        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == "--host" and i + 1 < len(sys.argv):
                host = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--port" and i + 1 < len(sys.argv):
                port = int(sys.argv[i + 1])
                i += 2
            elif sys.argv[i] == "--reload":
                reload = True
                i += 1
            else:
                i += 1
        
        run_web_server(host, port, reload)
    elif sys.argv[1] == "analyze":
        run_analysis(interactive=True)
    elif sys.argv[1] == "file" and len(sys.argv) > 2:
        run_analysis(input_file=sys.argv[2])
    else:
        print("Invalid command. Use: demo, cli, web, analyze, or file <path>")
