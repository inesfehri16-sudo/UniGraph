"""
UniGraph SPARQL Service
Executes SPARQL queries from .rq files or custom query strings against the RDF graph.
Formats results into clean, JSON-serializable dictionaries.
"""
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from rdflib import Graph
from src.config import QUERIES_DIR, RAW_GRAPH_FILE, INFERRED_GRAPH_FILE, bind_prefixes


class SPARQLService:
    def __init__(self, graph: Optional[Graph] = None, use_inferred: bool = False):
        self.use_inferred = use_inferred
        if graph is not None:
            self.graph = graph
        else:
            self.graph = Graph()
            bind_prefixes(self.graph)
            file_to_load = INFERRED_GRAPH_FILE if use_inferred and INFERRED_GRAPH_FILE.exists() else RAW_GRAPH_FILE
            self.graph.parse(str(file_to_load), format="turtle")

    def list_saved_queries(self) -> List[Dict[str, str]]:
        """Lists metadata of all predefined queries in the queries/ directory."""
        queries = []
        for p in sorted(QUERIES_DIR.glob("*.rq")):
            text = p.read_text(encoding="utf-8")
            description = ""
            for line in text.splitlines():
                if line.startswith("#"):
                    comment = line.lstrip("#").strip()
                    if comment:
                        description += (comment + " ")
                else:
                    break
            queries.append({
                "id": p.stem,
                "filename": p.name,
                "title": p.stem.replace("_", " ").title(),
                "description": description.strip(),
                "query": text
            })
        return queries

    def get_query_by_id(self, query_id: str) -> Optional[str]:
        """Loads query text from a specific query file."""
        candidates = list(QUERIES_DIR.glob(f"{query_id}.rq"))
        if candidates:
            return candidates[0].read_text(encoding="utf-8")
        return None

    def execute_query(self, query_str: str) -> Dict[str, Any]:
        """
        Executes a SPARQL query against the graph and returns structured JSON results.
        """
        start_time = time.time()
        try:
            results = self.graph.query(query_str)
            exec_time = time.time() - start_time

            vars_list = [str(v) for v in results.vars] if hasattr(results, "vars") and results.vars else []
            rows = []
            for row in results:
                row_dict = {}
                for var in vars_list:
                    val = getattr(row, var, None)
                    row_dict[var] = str(val) if val is not None else None
                rows.append(row_dict)

            return {
                "success": True,
                "variables": vars_list,
                "results": rows,
                "count": len(rows),
                "execution_time_seconds": round(exec_time, 4),
                "error": None
            }
        except Exception as e:
            exec_time = time.time() - start_time
            return {
                "success": False,
                "variables": [],
                "results": [],
                "count": 0,
                "execution_time_seconds": round(exec_time, 4),
                "error": str(e)
            }


if __name__ == "__main__":
    svc = SPARQLService(use_inferred=False)
    queries = svc.list_saved_queries()
    print(f"Found {len(queries)} predefined queries:")
    for q in queries:
        print(f" - {q['id']}: {q['title']}")
        res = svc.execute_query(q['query'])
        print(f"   Result count: {res['count']} (in {res['execution_time_seconds']}s)")
