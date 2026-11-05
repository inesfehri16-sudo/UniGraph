"""
Unit Tests: Ontology Structure and RDFS Axioms
"""
import pytest
from rdflib import RDF, RDFS, FOAF
from src.ontology import build_ontology
from src.config import UNIGRAPH


@pytest.fixture(scope="module")
def ontology_graph():
    return build_ontology()


def test_ontology_classes_count(ontology_graph):
    """Ontology must define at least 5 classes."""
    classes = list(ontology_graph.subjects(RDF.type, RDFS.Class))
    assert len(classes) >= 5, f"Expected >= 5 classes, found {len(classes)}"
    # Check specific core classes
    expected_classes = [
        UNIGRAPH.Person,
        UNIGRAPH.Student,
        UNIGRAPH.Instructor,
        UNIGRAPH.Department,
        UNIGRAPH.Course,
        UNIGRAPH.CourseSection,
        UNIGRAPH.Enrollment,
    ]
    for c in expected_classes:
        assert (c, RDF.type, RDFS.Class) in ontology_graph, f"Missing class {c}"


def test_ontology_properties_count(ontology_graph):
    """Ontology must define at least 8 properties."""
    properties = list(ontology_graph.subjects(RDF.type, RDF.Property))
    assert len(properties) >= 8, f"Expected >= 8 properties, found {len(properties)}"


def test_subclass_hierarchy(ontology_graph):
    """Verify rdfs:subClassOf hierarchies and FOAF reuse."""
    assert (UNIGRAPH.Person, RDFS.subClassOf, FOAF.Person) in ontology_graph
    assert (UNIGRAPH.Student, RDFS.subClassOf, UNIGRAPH.Person) in ontology_graph
    assert (UNIGRAPH.Instructor, RDFS.subClassOf, UNIGRAPH.Person) in ontology_graph
    assert (UNIGRAPH.Professor, RDFS.subClassOf, UNIGRAPH.Instructor) in ontology_graph
    assert (UNIGRAPH.Department, RDFS.subClassOf, FOAF.Organization) in ontology_graph


def test_subproperty_relationship(ontology_graph):
    """Ontology must define at least one rdfs:subPropertyOf relationship."""
    subprops = list(ontology_graph.triples((None, RDFS.subPropertyOf, None)))
    assert len(subprops) >= 1, "Expected at least 1 rdfs:subPropertyOf relationship"
    assert (UNIGRAPH.advises, RDFS.subPropertyOf, UNIGRAPH.supervises) in ontology_graph


def test_property_domains_and_ranges(ontology_graph):
    """Verify explicit rdfs:domain and rdfs:range definitions."""
    # unigraph:advises
    assert (UNIGRAPH.advises, RDFS.domain, UNIGRAPH.Instructor) in ontology_graph
    assert (UNIGRAPH.advises, RDFS.range, UNIGRAPH.Student) in ontology_graph

    # unigraph:supervises
    assert (UNIGRAPH.supervises, RDFS.domain, UNIGRAPH.Instructor) in ontology_graph
    assert (UNIGRAPH.supervises, RDFS.range, UNIGRAPH.Student) in ontology_graph

    # unigraph:enrolledInProgram
    assert (UNIGRAPH.enrolledInProgram, RDFS.domain, UNIGRAPH.Student) in ontology_graph
    assert (UNIGRAPH.enrolledInProgram, RDFS.range, UNIGRAPH.Program) in ontology_graph

    # unigraph:taughtBy
    assert (UNIGRAPH.taughtBy, RDFS.domain, UNIGRAPH.CourseSection) in ontology_graph
    assert (UNIGRAPH.taughtBy, RDFS.range, UNIGRAPH.Instructor) in ontology_graph
