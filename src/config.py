"""
UniGraph Configuration Module
Defines paths, namespaces, and graph prefix bindings.
"""
from pathlib import Path
from rdflib import Namespace
from rdflib.namespace import RDF, RDFS, XSD, FOAF

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
ONTOLOGY_DIR = BASE_DIR / "ontology"
QUERIES_DIR = BASE_DIR / "queries"
DOCS_DIR = BASE_DIR / "docs"

# RDF Output Files
ONTOLOGY_FILE = ONTOLOGY_DIR / "unigraph_ontology.ttl"
RAW_GRAPH_FILE = DATA_DIR / "unigraph.ttl"
INFERRED_GRAPH_FILE = DATA_DIR / "unigraph_inferred.ttl"
INFERRED_ONLY_FILE = DATA_DIR / "inferred_triples.ttl"

# Namespaces
UNIGRAPH = Namespace("https://unigraph.org/schema#")
DATA = Namespace("https://unigraph.org/data/")

def bind_prefixes(graph):
    """Bind common namespaces to a graph for clean Turtle serialization and SPARQL queries."""
    graph.bind("unigraph", UNIGRAPH)
    graph.bind("data", DATA)
    graph.bind("foaf", FOAF)
    graph.bind("rdf", RDF)
    graph.bind("rdfs", RDFS)
    graph.bind("xsd", XSD)
    return graph
