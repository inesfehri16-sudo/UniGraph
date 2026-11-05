"""
Unit Tests: Flask REST API Endpoints
Verifies that all required endpoints return valid JSON and appropriate HTTP status codes.
"""
import pytest
from src.api import create_app


@pytest.fixture(scope="module")
def client():
    app = create_app({"TESTING": True})
    with app.test_client() as client:
        yield client


def test_endpoint_status(client):
    """GET /api/status returns 200, valid JSON, and healthy status."""
    resp = client.get("/api/status")
    assert resp.status_code == 200
    assert resp.is_json
    data = resp.get_json()
    assert data["success"] is True
    assert data["data"]["status"] == "healthy"
    assert data["data"]["graph_statistics"]["raw_triples"] > 10000


def test_endpoint_ontology(client):
    """GET /api/ontology returns 200, valid JSON, classes, and properties."""
    resp = client.get("/api/ontology")
    assert resp.status_code == 200
    assert resp.is_json
    data = resp.get_json()
    assert data["success"] is True
    assert len(data["data"]["classes"]) >= 5
    assert len(data["data"]["properties"]) >= 8


def test_endpoint_students(client):
    """GET /api/students returns 200, valid JSON, and student list."""
    resp = client.get("/api/students?limit=10")
    assert resp.status_code == 200
    assert resp.is_json
    data = resp.get_json()
    assert data["success"] is True
    assert len(data["data"]) == 10
    first = data["data"][0]
    assert "studentName" in first
    assert "programName" in first


def test_endpoint_instructors(client):
    """GET /api/instructors returns 200, valid JSON, and 10 instructors."""
    resp = client.get("/api/instructors")
    assert resp.status_code == 200
    assert resp.is_json
    data = resp.get_json()
    assert data["success"] is True
    assert len(data["data"]) == 10
    first = data["data"][0]
    assert "instructorName" in first
    assert "departmentName" in first


def test_endpoint_departments(client):
    """GET /api/departments returns 200, valid JSON, and 14 departments."""
    resp = client.get("/api/departments")
    assert resp.status_code == 200
    assert resp.is_json
    data = resp.get_json()
    assert data["success"] is True
    assert data["count"] == 14
    first = data["data"][0]
    assert "name" in first
    assert "code" in first


def test_endpoint_programs(client):
    """GET /api/programs returns 200, valid JSON, and academic programs."""
    resp = client.get("/api/programs?limit=10")
    assert resp.status_code == 200
    assert resp.is_json
    data = resp.get_json()
    assert data["success"] is True
    assert len(data["data"]) == 10
    first = data["data"][0]
    assert "name" in first
    assert "departmentName" in first


def test_endpoint_courses(client):
    """GET /api/courses returns 200, valid JSON, and course records."""
    resp = client.get("/api/courses?limit=5")
    assert resp.status_code == 200
    assert resp.is_json
    data = resp.get_json()
    assert data["success"] is True
    assert len(data["data"]) == 5
    first = data["data"][0]
    assert "courseCode" in first
    assert "credits" in first


def test_endpoint_sections(client):
    """GET /api/sections returns 200, valid JSON, and 40 section records."""
    resp = client.get("/api/sections")
    assert resp.status_code == 200
    assert resp.is_json
    data = resp.get_json()
    assert data["success"] is True
    assert len(data["data"]) == 40


def test_endpoint_enrollments(client):
    """GET /api/enrollments returns 200, valid JSON, and enrollment records."""
    resp = client.get("/api/enrollments?limit=10")
    assert resp.status_code == 200
    assert resp.is_json
    data = resp.get_json()
    assert data["success"] is True
    assert len(data["data"]) == 10


def test_endpoint_sparql_queries_list(client):
    """GET /api/sparql/queries returns 200 and list of predefined queries."""
    resp = client.get("/api/sparql/queries")
    assert resp.status_code == 200
    assert resp.is_json
    data = resp.get_json()
    assert data["success"] is True
    assert data["count"] >= 5


def test_endpoint_sparql_execute_predefined(client):
    """POST /api/sparql/execute with query_id returns 200 and query results."""
    resp = client.post("/api/sparql/execute", json={"query_id": "q1_students_programs"})
    assert resp.status_code == 200
    assert resp.is_json
    data = resp.get_json()
    assert data["success"] is True
    assert data["count"] == 50


def test_endpoint_sparql_execute_custom(client):
    """POST /api/sparql/execute with custom query string returns 200."""
    custom_q = """
    PREFIX unigraph: <https://unigraph.org/schema#>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    SELECT ?d ?name WHERE { ?d a unigraph:Department ; foaf:name ?name } LIMIT 3
    """
    resp = client.post("/api/sparql/execute", json={"query": custom_q})
    assert resp.status_code == 200
    assert resp.is_json
    data = resp.get_json()
    assert data["success"] is True
    assert data["count"] == 3


def test_endpoint_sparql_execute_invalid_syntax(client):
    """POST /api/sparql/execute with invalid syntax returns 400."""
    resp = client.post("/api/sparql/execute", json={"query": "THIS IS NOT SPARQL"})
    assert resp.status_code == 400
    assert resp.is_json
    data = resp.get_json()
    assert data["success"] is False
    assert "error" in data


def test_endpoint_inference_demo(client):
    """GET /api/inference/demo returns 200 and RDFS before/after metrics."""
    resp = client.get("/api/inference/demo")
    assert resp.status_code == 200
    assert resp.is_json
    data = resp.get_json()
    assert data["success"] is True
    demos = data["data"]["demonstrations"]
    assert "demo1_subproperty_supervises" in demos
    assert "demo2_subclass_foaf_person" in demos


def test_endpoint_invalid_limit(client):
    """GET /api/students with invalid limit parameter returns 400."""
    resp1 = client.get("/api/students?limit=-5")
    assert resp1.status_code == 400
    assert resp1.get_json()["success"] is False

    resp2 = client.get("/api/students?limit=abc")
    assert resp2.status_code == 400
    assert resp2.get_json()["success"] is False


def test_endpoint_sparql_missing_body(client):
    """POST /api/sparql/execute with empty body returns 400."""
    resp = client.post("/api/sparql/execute", json={})
    assert resp.status_code == 400
    assert resp.get_json()["success"] is False


def test_endpoint_sparql_unknown_query_id(client):
    """POST /api/sparql/execute with nonexistent query_id returns 404."""
    resp = client.post("/api/sparql/execute", json={"query_id": "nonexistent_query_999"})
    assert resp.status_code == 404
    assert resp.get_json()["success"] is False


def test_endpoint_sparql_non_dict_body(client):
    """POST /api/sparql/execute with non-dict JSON body returns 400."""
    resp = client.post("/api/sparql/execute", data="[1, 2, 3]", content_type="application/json")
    assert resp.status_code == 400
    assert resp.get_json()["success"] is False


def test_endpoint_export_inferred_only(client):
    """GET /api/export/inferred_only returns 200."""
    resp = client.get("/api/export/inferred_only")
    assert resp.status_code == 200


def test_endpoint_404_handling(client):
    """GET /api/nonexistent returns 404 with JSON error structure."""
    resp = client.get("/api/nonexistent")
    assert resp.status_code == 404
    assert resp.is_json
    data = resp.get_json()
    assert data["success"] is False
    assert data["status"] == 404
