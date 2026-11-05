"""
UniGraph RDFS Inference Module
Performs standard W3C RDFS deductive closure using RDFLib and OWL-RL.
Separates raw triples from inferred triples and exposes reproducible before/after demonstrations.
"""
from typing import Dict, Any, Tuple
from rdflib import Graph, RDF, RDFS, FOAF
import owlrl

from src.config import (
    RAW_GRAPH_FILE,
    INFERRED_GRAPH_FILE,
    INFERRED_ONLY_FILE,
    UNIGRAPH,
    bind_prefixes,
)


def run_inference(raw_graph: Graph = None, save_files: bool = True) -> Tuple[Graph, Graph]:
    """
    Executes RDFS deductive closure on the knowledge graph.
    Returns:
        (expanded_graph, inferred_only_graph)
    """
    if raw_graph is None:
        raw_graph = Graph()
        bind_prefixes(raw_graph)
        raw_graph.parse(str(RAW_GRAPH_FILE), format="turtle")

    # Clone for expansion
    expanded_graph = Graph()
    bind_prefixes(expanded_graph)
    for t in raw_graph:
        expanded_graph.add(t)

    # Perform RDFS deductive closure
    owlrl.DeductiveClosure(owlrl.RDFS_Semantics).expand(expanded_graph)

    # Calculate newly inferred triples
    inferred_only_graph = Graph()
    bind_prefixes(inferred_only_graph)
    raw_triples_set = set(raw_graph)
    for t in expanded_graph:
        if t not in raw_triples_set:
            inferred_only_graph.add(t)

    if save_files:
        INFERRED_GRAPH_FILE.parent.mkdir(parents=True, exist_ok=True)
        expanded_graph.serialize(destination=str(INFERRED_GRAPH_FILE), format="turtle")
        inferred_only_graph.serialize(destination=str(INFERRED_ONLY_FILE), format="turtle")

    return expanded_graph, inferred_only_graph


def get_inference_demonstrations(raw_g: Graph = None, exp_g: Graph = None) -> Dict[str, Any]:
    """
    Evaluates and formats explicit before-and-after demonstrations
    for the academic report, presentation, REST API, and tests.
    """
    if raw_g is None:
        raw_g = Graph()
        bind_prefixes(raw_g)
        raw_g.parse(str(RAW_GRAPH_FILE), format="turtle")

    if exp_g is None:
        if INFERRED_GRAPH_FILE.exists():
            exp_g = Graph()
            bind_prefixes(exp_g)
            exp_g.parse(str(INFERRED_GRAPH_FILE), format="turtle")
        else:
            exp_g, _ = run_inference(raw_g, save_files=True)

    # Demo 1: Subproperty advises -> supervises (Rule rdfs7)
    raw_supervises = list(raw_g.triples((None, UNIGRAPH.supervises, None)))
    exp_supervises = list(exp_g.triples((None, UNIGRAPH.supervises, None)))

    # Demo 2: Subclass Student & Instructor -> Person -> foaf:Person (Rule rdfs9)
    raw_foaf_persons = list(raw_g.triples((None, RDF.type, FOAF.Person)))
    exp_foaf_persons = list(exp_g.triples((None, RDF.type, FOAF.Person)))

    raw_unigraph_persons = list(raw_g.triples((None, RDF.type, UNIGRAPH.Person)))
    exp_unigraph_persons = list(exp_g.triples((None, RDF.type, UNIGRAPH.Person)))

    # Demo 3: Subproperty enrolledInSection -> involvedInCourse (Rule rdfs7)
    raw_involved = list(raw_g.triples((None, UNIGRAPH.involvedInCourse, None)))
    exp_involved = list(exp_g.triples((None, UNIGRAPH.involvedInCourse, None)))

    # Demo 4: Subclass Professor -> Instructor (Rule rdfs9)
    raw_instructors = list(raw_g.triples((None, RDF.type, UNIGRAPH.Instructor)))
    exp_instructors = list(exp_g.triples((None, RDF.type, UNIGRAPH.Instructor)))

    demos = {
        "demo1_subproperty_supervises": {
            "title": "Subproperty Inference: unigraph:advises -> unigraph:supervises",
            "rule": "rdfs7",
            "rule_name": "Subproperty Inheritance",
            "formal_definition": "(?p rdfs:subPropertyOf ?q) ∧ (?s ?p ?o) ⟹ (?s ?q ?o)",
            "axiom": "unigraph:advises rdfs:subPropertyOf unigraph:supervises",
            "description": "In the raw dataset, only 'unigraph:advises' is asserted when linking an advisor instructor to a student. Because 'advises' is declared as an rdfs:subPropertyOf 'supervises', the reasoner automatically infers that the instructor also supervises the student.",
            "before_count": len(raw_supervises),
            "after_count": len(exp_supervises),
            "inferred_count": len(exp_supervises) - len(raw_supervises),
            "sample_triples": [
                {
                    "subject": str(s),
                    "predicate": "unigraph:supervises",
                    "object": str(o)
                }
                for s, _, o in exp_supervises[:5]
            ]
        },
        "demo2_subclass_foaf_person": {
            "title": "Subclass Hierarchy Propagation: Student & Instructor -> foaf:Person",
            "rule": "rdfs9",
            "rule_name": "Class Membership Propagation",
            "formal_definition": "(?c rdfs:subClassOf ?d) ∧ (?x rdf:type ?c) ⟹ (?x rdf:type ?d)",
            "axiom": "unigraph:Student rdfs:subClassOf unigraph:Person ∧ unigraph:Person rdfs:subClassOf foaf:Person",
            "description": "In the raw graph, individuals are only typed as 'unigraph:Student' or specific instructor types ('unigraph:Professor', 'unigraph:Lecturer'). They are never asserted directly as 'foaf:Person'. Through 2 transitive steps of rdfs9, all 50 students and 10 instructors are inferred to be members of foaf:Person.",
            "before_count": len(raw_foaf_persons),
            "after_count": len(exp_foaf_persons),
            "inferred_count": len(exp_foaf_persons) - len(raw_foaf_persons),
            "sample_triples": [
                {
                    "subject": str(s),
                    "predicate": "rdf:type",
                    "object": "foaf:Person"
                }
                for s, _, _ in exp_foaf_persons[:5]
            ]
        },
        "demo3_subproperty_involved": {
            "title": "Subproperty Inference: enrolledInSection -> involvedInCourse",
            "rule": "rdfs7",
            "rule_name": "Subproperty Inheritance",
            "formal_definition": "(?p rdfs:subPropertyOf ?q) ∧ (?s ?p ?o) ⟹ (?s ?q ?o)",
            "axiom": "unigraph:enrolledInSection rdfs:subPropertyOf unigraph:involvedInCourse",
            "description": "All 1,000 student-section enrollments asserted with 'enrolledInSection' are automatically inferred to also instantiate the high-level 'involvedInCourse' relationship.",
            "before_count": len(raw_involved),
            "after_count": len(exp_involved),
            "inferred_count": len(exp_involved) - len(raw_involved),
            "sample_triples": [
                {
                    "subject": str(s),
                    "predicate": "unigraph:involvedInCourse",
                    "object": str(o)
                }
                for s, _, o in exp_involved[:5]
            ]
        },
        "demo4_subclass_instructor": {
            "title": "Subclass Propagation: Professor/Lecturer -> unigraph:Instructor",
            "rule": "rdfs9",
            "rule_name": "Class Membership Propagation",
            "formal_definition": "(?c rdfs:subClassOf ?d) ∧ (?x rdf:type ?c) ⟹ (?x rdf:type ?d)",
            "axiom": "unigraph:Professor rdfs:subClassOf unigraph:Instructor",
            "description": "Instructors recorded with rank professor, associate_professor, or assistant_professor were asserted with class Professor. Rule rdfs9 infers their membership in class Instructor.",
            "before_count": len(raw_instructors),
            "after_count": len(exp_instructors),
            "inferred_count": len(exp_instructors) - len(raw_instructors),
            "sample_triples": [
                {
                    "subject": str(s),
                    "predicate": "rdf:type",
                    "object": "unigraph:Instructor"
                }
                for s, _, _ in exp_instructors[:5]
            ]
        }
    }

    return {
        "raw_triple_count": len(raw_g),
        "total_inferred_triple_count": len(exp_g),
        "newly_inferred_triples": len(exp_g) - len(raw_g),
        "demonstrations": demos
    }


if __name__ == "__main__":
    print("Running RDFS inference engine...")
    exp_g, inf_only_g = run_inference(save_files=True)
    print(f"RDFS inference complete! Inferred graph: {len(exp_g)} triples, New triples: {len(inf_only_g)}.")
    demos = get_inference_demonstrations(exp_g=exp_g)
    for k, d in demos["demonstrations"].items():
        print(f"[{d['rule']}] {d['title']}: Before={d['before_count']} -> After={d['after_count']} (Delta: +{d['inferred_count']})")
