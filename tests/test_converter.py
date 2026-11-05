"""
Unit Tests: CSV to RDF Conversion and Traceability
"""
import pytest
from rdflib import Graph, RDF, RDFS, FOAF
from src.converter import convert_csv_to_rdf
from src.config import RAW_GRAPH_FILE, UNIGRAPH, DATA


@pytest.fixture(scope="module")
def raw_graph():
    if RAW_GRAPH_FILE.exists():
        g = Graph()
        g.parse(str(RAW_GRAPH_FILE), format="turtle")
        return g
    return convert_csv_to_rdf(save_to_file=True)


def test_triple_count(raw_graph):
    """Ensure the converted RDF graph contains a substantial number of triples."""
    assert len(raw_graph) > 10000, f"Expected > 10,000 triples, got {len(raw_graph)}"


def test_entity_types_present(raw_graph):
    """Ensure all core entity types exist in the generated graph."""
    students = list(raw_graph.subjects(RDF.type, UNIGRAPH.Student))
    courses = list(raw_graph.subjects(RDF.type, UNIGRAPH.Course))
    sections = list(raw_graph.subjects(RDF.type, UNIGRAPH.CourseSection))
    enrollments = list(raw_graph.subjects(RDF.type, UNIGRAPH.Enrollment))
    departments = list(raw_graph.subjects(RDF.type, UNIGRAPH.Department))
    programs = list(raw_graph.subjects(RDF.type, UNIGRAPH.Program))
    semesters = list(raw_graph.subjects(RDF.type, UNIGRAPH.Semester))

    assert len(students) == 50, f"Expected 50 students, got {len(students)}"
    assert len(courses) == 600, f"Expected 600 courses, got {len(courses)}"
    assert len(sections) == 40, f"Expected 40 sections, got {len(sections)}"
    assert len(enrollments) == 1000, f"Expected 1000 enrollments, got {len(enrollments)}"
    assert len(departments) == 14, f"Expected 14 departments, got {len(departments)}"
    assert len(programs) == 40, f"Expected 40 programs, got {len(programs)}"
    assert len(semesters) == 10, f"Expected 10 semesters, got {len(semesters)}"


def test_source_id_traceability(raw_graph):
    """Verify that sourceId properties link entities back to CSV IDs."""
    source_ids = list(raw_graph.subject_objects(UNIGRAPH.sourceId))
    assert len(source_ids) > 1000, "Traceability sourceId triples must be present."
    # Check student 1
    stud_1 = DATA["student/1"]
    assert any(o for s, o in raw_graph.predicate_objects(stud_1) if s == UNIGRAPH.sourceId)


def test_foaf_integration(raw_graph):
    """Verify FOAF properties are attached to students and instructors."""
    stud_names = list(raw_graph.subject_objects(FOAF.name))
    assert len(stud_names) >= 60, "Students and instructors must have foaf:name attached."

    mboxes = list(raw_graph.subject_objects(FOAF.mbox))
    assert len(mboxes) >= 60, "People must have foaf:mbox attached."
