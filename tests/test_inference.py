"""
Unit Tests: RDFS Inference Engine and Semantic Axiom Rules
"""
import pytest
from src.inference import get_inference_demonstrations, run_inference
from src.config import INFERRED_GRAPH_FILE, INFERRED_ONLY_FILE


@pytest.fixture(scope="module")
def inference_data():
    return get_inference_demonstrations()


def test_inferred_triples_exist(inference_data):
    """Verify that RDFS deductive closure inferred new triples."""
    assert inference_data["newly_inferred_triples"] > 1000
    assert inference_data["total_inferred_triple_count"] > inference_data["raw_triple_count"]
    assert INFERRED_GRAPH_FILE.exists()
    assert INFERRED_ONLY_FILE.exists()


def test_demo1_subproperty_supervises(inference_data):
    """
    Demo 1 (Rule rdfs7): unigraph:advises rdfs:subPropertyOf unigraph:supervises
    Before inference: 0 unigraph:supervises triples.
    After inference: exactly 50 unigraph:supervises triples.
    """
    demo = inference_data["demonstrations"]["demo1_subproperty_supervises"]
    assert demo["rule"] == "rdfs7"
    assert demo["before_count"] == 0, f"Expected 0 before inference, got {demo['before_count']}"
    assert demo["after_count"] == 50, f"Expected 50 after inference, got {demo['after_count']}"
    assert demo["inferred_count"] == 50
    assert len(demo["sample_triples"]) > 0


def test_demo2_subclass_foaf_person(inference_data):
    """
    Demo 2 (Rule rdfs9): Student & Instructor -> unigraph:Person -> foaf:Person
    Before inference: 0 foaf:Person asserted directly.
    After inference: exactly 60 foaf:Person instances (50 students + 10 instructors).
    """
    demo = inference_data["demonstrations"]["demo2_subclass_foaf_person"]
    assert demo["rule"] == "rdfs9"
    assert demo["before_count"] == 0, f"Expected 0 before inference, got {demo['before_count']}"
    assert demo["after_count"] == 60, f"Expected 60 after inference, got {demo['after_count']}"
    assert demo["inferred_count"] == 60


def test_demo3_subproperty_involved(inference_data):
    """
    Demo 3 (Rule rdfs7): enrolledInSection rdfs:subPropertyOf involvedInCourse
    Before inference: 0 involvedInCourse.
    After inference: 1000 involvedInCourse triples.
    """
    demo = inference_data["demonstrations"]["demo3_subproperty_involved"]
    assert demo["rule"] == "rdfs7"
    assert demo["before_count"] == 0
    assert demo["after_count"] == 1000
    assert demo["inferred_count"] == 1000


def test_demo4_subclass_instructor(inference_data):
    """
    Demo 4 (Rule rdfs9): Professor / Lecturer -> Instructor
    """
    demo = inference_data["demonstrations"]["demo4_subclass_instructor"]
    assert demo["rule"] == "rdfs9"
    assert demo["before_count"] == 0
    assert demo["after_count"] == 10
    assert demo["inferred_count"] == 10


def test_semantic_cleanliness(inference_data):
    """
    Verify that RDFS inference does NOT produce spurious inferences:
    - Programs must NOT be inferred as Course instances.
    - Departments must NOT be inferred as CourseSection instances.
    """
    clean_checks = inference_data["semantic_cleanliness_checks"]
    assert clean_checks["programs_falsely_typed_as_courses"] == 0
    assert clean_checks["departments_falsely_typed_as_sections"] == 0
    assert clean_checks["is_semantically_sound"] is True
