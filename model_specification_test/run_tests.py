"""
Main test runner for model specification tests
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import MODELS, DEFAULT_MODEL, TEST_CONFIG, OUTPUT_DIR, RAW_DIR, REPORT_DIR
from utils.scoring import aggregate_scores
from utils.report import generate_markdown_report, generate_json_report, generate_comparison_report

# Import test modules
from tests import (
    test_tool_calling,
    test_rag,
    test_code_execution,
    test_vision,
    test_json_mode,
    test_structured_output,
    test_multiturn,
    test_streaming,
    test_cot_reasoning,
    test_agent,
    test_web_search,
    test_terminal,
    test_file_ops,
    test_memory,
    test_task_planning,
    test_cron,
    test_messaging,
    test_session_search,
    test_clarifying,
    test_delegation,
    test_skills,
    test_context_engine,
    test_mixture_of_agents,
)


def run_all_tests(model_name: str = None) -> Dict[str, Any]:
    """Run all tests for a specific model."""
    
    if model_name is None:
        model_name = DEFAULT_MODEL
    
    if model_name not in MODELS:
        print(f"Error: Model '{model_name}' not found in configuration")
        return {}
    
    model_config = MODELS[model_name]
    
    if not model_config.get("enabled", False):
        print(f"Error: Model '{model_name}' is not enabled in configuration")
        return {}
    
    print(f"\n{'='*60}")
    print(f"Running tests for model: {model_name}")
    print(f"{'='*60}\n")
    
    # Initialize OpenAI client
    from openai import OpenAI
    client = OpenAI(
        base_url=model_config["base_url"],
        api_key=model_config["api_key"]
    )
    
    # Run all test modules
    test_modules = [
        ("Tool Calling", test_tool_calling),
        ("RAG", test_rag),
        ("Code Execution", test_code_execution),
        ("Vision", test_vision),
        ("JSON Mode", test_json_mode),
        ("Structured Output", test_structured_output),
        ("Multi-turn", test_multiturn),
        ("Streaming", test_streaming),
        ("Chain-of-Thought", test_cot_reasoning),
        ("Agent", test_agent),
        ("Web Search", test_web_search),
        ("Terminal", test_terminal),
        ("File Operations", test_file_ops),
        ("Memory", test_memory),
        ("Task Planning", test_task_planning),
        ("Cron", test_cron),
        ("Messaging", test_messaging),
        ("Session Search", test_session_search),
        ("Clarifying", test_clarifying),
        ("Delegation", test_delegation),
        ("Skills", test_skills),
        ("Context Engine", test_context_engine),
        ("Mixture of Agents", test_mixture_of_agents),
    ]
    
    results = []
    
    for test_name, test_module in test_modules:
        print(f"Running {test_name} tests...")
        try:
            result = test_module.run_test(client, model_name, TEST_CONFIG)
            results.append(result)
            print(f"  ✓ Score: {result.get('score', 0.0):.3f}")
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            results.append({
                "capability": test_name,
                "score": 0.0,
                "error": str(e)
            })
        
        # Small delay between tests to let GPU memory release
        import time
        time.sleep(0.5)
    
    # Aggregate results
    aggregated = aggregate_scores(results)
    
    # Create output directories
    Path(RAW_DIR).mkdir(parents=True, exist_ok=True)
    Path(REPORT_DIR).mkdir(parents=True, exist_ok=True)
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Sanitize model name for filename (replace / and : with _)
    safe_model_name = model_name.replace("/", "_").replace(":", "_")
    
    # Save raw results
    raw_path = Path(RAW_DIR) / f"{safe_model_name}_{timestamp}.json"
    raw_data = {
        "model_name": model_name,
        "test_date": datetime.now().isoformat(),
        "results": results,
        "summary": aggregated
    }
    raw_path.write_text(json.dumps(raw_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n✓ Raw results saved to: {raw_path}")
    
    # Generate markdown report
    md_path = Path(REPORT_DIR) / f"{safe_model_name}_{timestamp}.md"
    generate_markdown_report(model_name, results, str(md_path))
    print(f"✓ Markdown report saved to: {md_path}")
    
    # Generate JSON report
    json_path = Path(REPORT_DIR) / f"{safe_model_name}_{timestamp}.json"
    generate_json_report(model_name, results, str(json_path))
    print(f"✓ JSON report saved to: {json_path}")
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Test Summary for {model_name}")
    print(f"{'='*60}")
    print(f"Total Score: {aggregated['total_score']:.3f}")
    print(f"Average Score: {aggregated['average_score']:.3f}")
    print(f"Total Tests: {aggregated['total_tests']}")
    print(f"Passed: {aggregated['passed_tests']}")
    print(f"Failed: {aggregated['failed_tests']}")
    print(f"Pass Rate: {aggregated['pass_rate']:.1%}")
    print(f"{'='*60}\n")
    
    return raw_data


def run_comparison(models: List[str] = None) -> Dict[str, Any]:
    """Run tests for multiple models and generate comparison report."""
    
    if models is None:
        # Use all enabled models
        models = [name for name, config in MODELS.items() if config.get("enabled", False)]
    
    if not models:
        print("Error: No enabled models found in configuration")
        return {}
    
    print(f"\n{'='*60}")
    print(f"Running comparison tests for {len(models)} models")
    print(f"{'='*60}\n")
    
    results_by_model = {}
    
    for model_name in models:
        print(f"\nTesting model: {model_name}")
        result = run_all_tests(model_name)
        if result:
            results_by_model[model_name] = result.get("results", [])
    
    if not results_by_model:
        print("Error: No results generated")
        return {}
    
    # Generate comparison report
    Path(REPORT_DIR).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    comparison_path = Path(REPORT_DIR) / f"comparison_{timestamp}.md"
    
    generate_comparison_report(results_by_model, str(comparison_path))
    print(f"\n✓ Comparison report saved to: {comparison_path}")
    
    return results_by_model


def get_running_models() -> List[str]:
    """Auto-detect which models are currently running by reading actual model names from server.
    
    - Ollama: uses /api/ps to get only LOADED models (not all downloaded)
    - llama.cpp: uses /v1/models (only returns the single loaded model)
    """
    import urllib.request
    import urllib.error
    
    # Snapshot endpoints to check (avoid modifying dict during iteration)
    endpoints = []
    seen_urls = set()
    for name, config in list(MODELS.items()):
        base_url = config["base_url"]
        if base_url not in seen_urls:
            seen_urls.add(base_url)
            endpoints.append((base_url, config["api_key"], config["platform"]))
    
    running = []
    new_models = {}
    
    for base_url, api_key, platform in endpoints:
        try:
            if platform == "ollama":
                # Ollama: use /api/ps to get only LOADED/running models
                ollama_base = base_url.replace("/v1", "")
                url = f"{ollama_base}/api/ps"
                req = urllib.request.Request(url, method="GET")
                with urllib.request.urlopen(req, timeout=3) as response:
                    if response.status == 200:
                        data = json.loads(response.read().decode("utf-8"))
                        models_data = data.get("models", [])
                        for model_entry in models_data:
                            actual_model_name = model_entry.get("name", model_entry.get("model", ""))
                            if not actual_model_name:
                                continue
                            if actual_model_name in running:
                                continue
                            running.append(actual_model_name)
                            if actual_model_name not in MODELS and actual_model_name not in new_models:
                                new_models[actual_model_name] = {
                                    "base_url": base_url,
                                    "api_key": api_key,
                                    "platform": platform,
                                    "enabled": True,
                                }
                                print(f"  → Auto-registered: {actual_model_name} ({platform}) at {base_url}")
            else:
                # llama.cpp: /v1/models returns only the loaded model
                url = f"{base_url}/models"
                req = urllib.request.Request(url, method="GET")
                with urllib.request.urlopen(req, timeout=3) as response:
                    if response.status == 200:
                        data = json.loads(response.read().decode("utf-8"))
                        models_data = data.get("data", data.get("models", []))
                        for model_entry in models_data:
                            actual_model_name = model_entry.get("id", model_entry.get("name", ""))
                            if not actual_model_name:
                                continue
                            if actual_model_name in running:
                                continue
                            running.append(actual_model_name)
                            if actual_model_name not in MODELS and actual_model_name not in new_models:
                                new_models[actual_model_name] = {
                                    "base_url": base_url,
                                    "api_key": api_key,
                                    "platform": platform,
                                    "enabled": True,
                                }
                                print(f"  → Auto-registered: {actual_model_name} ({platform}) at {base_url}")
        except (urllib.error.URLError, urllib.error.HTTPError, Exception) as e:
            print(f"  ✗ Could not reach {base_url}: {e}")
    
    # Add newly discovered models to MODELS after iteration is done
    MODELS.update(new_models)
    
    return running

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Model Specification Test Runner")
    parser.add_argument("--model", type=str, help="Model name to test")
    parser.add_argument("--platform", type=str, choices=["ollama", "llama.cpp", "all"], help="Filter by platform")
    parser.add_argument("--compare", action="store_true", help="Run comparison across models")
    parser.add_argument("--list-models", action="store_true", help="List available models")
    parser.add_argument("--auto", action="store_true", help="Auto-detect and test running models")
    
    args = parser.parse_args()
    
    if args.list_models:
        print("\nAvailable models:")
        for name, config in MODELS.items():
            enabled = "✓" if config.get("enabled", False) else "✗"
            print(f"  {enabled} {name} ({config['platform']})")
        print()
        return
    
    if args.auto:
        running = get_running_models()
        if not running:
            print("No running models detected. Check if Ollama or llama-server is running.")
            return
        
        if len(running) == 1:
            print(f"Auto-detected running model: {running[0]}")
            run_all_tests(running[0])
            return
        
        # Multiple models detected — let user choose
        print(f"\nAuto-detected {len(running)} running models:\n")
        for i, model_name in enumerate(running, 1):
            config = MODELS.get(model_name, {})
            platform = config.get("platform", "unknown")
            base_url = config.get("base_url", "unknown")
            print(f"  [{i}] {model_name} ({platform}) @ {base_url}")
        print(f"  [a] Test ALL models (comparison)")
        print(f"  [q] Quit")
        
        while True:
            try:
                choice = input(f"\nSelect model to test [1-{len(running)}/a/q]: ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\nAborted.")
                return
            
            if choice == 'q':
                return
            elif choice == 'a':
                # Run comparison on all detected models
                results_by_model = {}
                for model_name in running:
                    print(f"\nTesting model: {model_name}")
                    result = run_all_tests(model_name)
                    if result:
                        results_by_model[model_name] = result.get("results", [])
                
                if results_by_model:
                    Path(REPORT_DIR).mkdir(parents=True, exist_ok=True)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    comparison_path = Path(REPORT_DIR) / f"comparison_{timestamp}.md"
                    generate_comparison_report(results_by_model, str(comparison_path))
                    print(f"\n✓ Comparison report saved to: {comparison_path}")
                return
            elif choice.isdigit() and 1 <= int(choice) <= len(running):
                selected = running[int(choice) - 1]
                print(f"\nSelected: {selected}")
                run_all_tests(selected)
                return
            else:
                print(f"Invalid choice. Enter 1-{len(running)}, 'a' for all, or 'q' to quit.")

    if args.compare:
        if args.platform:
            models_to_test = [name for name, config in MODELS.items() if config.get("platform") == args.platform and config.get("enabled")]
        else:
            models_to_test = [name for name, config in MODELS.items() if config.get("enabled")]
        
        if not models_to_test:
            print(f"No enabled models found for platform: {args.platform or 'any'}")
            return
            
        print(f"Running comparison for: {', '.join(models_to_test)}")
        # Override run_comparison to use specific models
        results_by_model = {}
        for model_name in models_to_test:
            print(f"\nTesting model: {model_name}")
            result = run_all_tests(model_name)
            if result:
                results_by_model[model_name] = result.get("results", [])
        
        if not results_by_model:
            print("Error: No results generated")
            return
        
        Path(REPORT_DIR).mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        comparison_path = Path(REPORT_DIR) / f"comparison_{timestamp}.md"
        generate_comparison_report(results_by_model, str(comparison_path))
        print(f"\n✓ Comparison report saved to: {comparison_path}")
        return

    if args.platform:
        models_to_test = [name for name, config in MODELS.items() if config.get("platform") == args.platform and config.get("enabled")]
        if not models_to_test:
            print(f"No enabled models found for platform: {args.platform}")
            return
        model_name = models_to_test[0]
        print(f"Selected model from platform '{args.platform}': {model_name}")
    else:
        model_name = args.model if args.model else DEFAULT_MODEL
        
    run_all_tests(model_name)


if __name__ == "__main__":
    main()
