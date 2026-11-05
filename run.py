"""
UniGraph CLI & Main Entrypoint
Unified command runner for building, inferring, testing, and serving UniGraph.
"""
import sys
import argparse
import subprocess
from pathlib import Path


def cmd_build():
    print("=== [1/2] Building UniGraph Ontology ===")
    from src.ontology import save_ontology
    save_ontology()
    print("=== [2/2] Converting CSV Records to RDF (Turtle) ===")
    from src.converter import convert_csv_to_rdf
    convert_csv_to_rdf(save_to_file=True)
    print("Build complete!")


def cmd_infer():
    print("=== Running RDFS Deductive Closure Inference ===")
    from src.inference import run_inference, get_inference_demonstrations
    exp_g, inf_only_g = run_inference(save_files=True)
    print(f"Inference complete: Total triples = {len(exp_g)}, Newly inferred = {len(inf_only_g)}")
    demos = get_inference_demonstrations(exp_g=exp_g)
    for k, d in demos["demonstrations"].items():
        print(f" - [{d['rule']}] {d['title']}: {d['before_count']} -> {d['after_count']} (+{d['inferred_count']})")


def cmd_visualize():
    print("=== Generating Ontology Visualizations ===")
    from src.visualizer import build_all_diagrams
    build_all_diagrams()
    print("Diagrams generated in ontology/ and docs/ (SVG, PNG, DOT, MMD)!")


def cmd_test():
    print("=== Running Automated Pytest Suite ===")
    res = subprocess.run([sys.executable, "-m", "pytest", "-v"])
    sys.exit(res.returncode)


def cmd_query(query_id: str, use_inferred: bool = False):
    from src.sparql_service import SPARQLService
    svc = SPARQLService(use_inferred=use_inferred)
    q_text = svc.get_query_by_id(query_id)
    if not q_text:
        print(f"Error: Query '{query_id}' not found in queries/ directory.")
        sys.exit(1)
    print(f"=== Executing Query '{query_id}' (Inferred: {use_inferred}) ===")
    res = svc.execute_query(q_text)
    if res["success"]:
        print(f"Results: {res['count']} rows in {res['execution_time_seconds']}s")
        for row in res["results"][:10]:
            print(row)
        if res["count"] > 10:
            print(f"... and {res['count'] - 10} more rows.")
    else:
        print(f"Error: {res['error']}")


def cmd_serve(host: str = "127.0.0.1", port: int = 5000):
    from src.api import create_app
    app = create_app()
    print(f"\n=======================================================")
    print(f"  UniGraph Knowledge Graph REST API & Web Dashboard")
    print(f"  URL: http://{host}:{port}")
    print(f"=======================================================\n")
    app.run(host=host, port=port, debug=False)


def main():
    parser = argparse.ArgumentParser(description="UniGraph Knowledge Graph Manager")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    subparsers.add_parser("build", help="Build ontology and convert CSV to RDF")
    subparsers.add_parser("infer", help="Run RDFS inference and export inferred graph")
    subparsers.add_parser("visualize", help="Generate SVG, PNG, and DOT diagrams")
    subparsers.add_parser("test", help="Run pytest automated test suite")
    subparsers.add_parser("all", help="Run build, infer, visualize, and test in sequence")

    query_parser = subparsers.add_parser("query", help="Execute a predefined SPARQL query")
    query_parser.add_argument("query_id", help="Query identifier (e.g. q1_students_programs)")
    query_parser.add_argument("--inferred", action="store_true", help="Execute on inferred graph")

    serve_parser = subparsers.add_parser("serve", help="Start Flask REST API & Web Dashboard")
    serve_parser.add_argument("--host", default="127.0.0.1", help="Host interface (default 127.0.0.1)")
    serve_parser.add_argument("--port", type=int, default=5000, help="Port (default 5000)")

    args = parser.parse_args()

    if args.command == "build":
        cmd_build()
    elif args.command == "infer":
        cmd_infer()
    elif args.command == "visualize":
        cmd_visualize()
    elif args.command == "test":
        cmd_test()
    elif args.command == "query":
        cmd_query(args.query_id, args.inferred)
    elif args.command == "serve":
        cmd_serve(args.host, args.port)
    elif args.command == "all":
        cmd_build()
        cmd_infer()
        cmd_visualize()
        cmd_test()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
