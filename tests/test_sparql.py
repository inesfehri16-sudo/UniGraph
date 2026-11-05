"""
Unit Tests: SPARQL Predefined and Custom Queries
"""
import pytest
from src.sparql_service import SPARQLService


@pytest.fixture(scope="module")
def sparql_service():
    return SPARQLService(use_inferred=False)


def test_list_queries(sparql_service):
    """Ensure at least 5 SPARQL queries are defined in queries/ directory."""
    queries = sparql_service.list_saved_queries()
    assert len(queries) >= 5, f"Expected >= 5 queries, found {len(queries)}"


def test_query1_students_programs(sparql_service):
    """Query 1: Students and Programs must return 50 rows."""
    q_text = sparql_service.get_query_by_id("q1_students_programs")
    assert q_text is not None
    res = sparql_service.execute_query(q_text)
    assert res["success"] is True
    assert res["count"] == 50
    assert "studentName" in res["variables"]
    assert "programName" in res["variables"]


def test_query2_instructors_departments(sparql_service):
    """Query 2: Instructors and Departments must return 10 rows."""
    q_text = sparql_service.get_query_by_id("q2_instructors_departments")
    assert q_text is not None
    res = sparql_service.execute_query(q_text)
    assert res["success"] is True
    assert res["count"] == 10
    assert "instructorName" in res["variables"]
    assert "departmentName" in res["variables"]


def test_query3_courses_departments(sparql_service):
    """Query 3: Courses and Departments must return 600 rows."""
    q_text = sparql_service.get_query_by_id("q3_courses_departments")
    assert q_text is not None
    res = sparql_service.execute_query(q_text)
    assert res["success"] is True
    assert res["count"] == 600
    assert "courseCode" in res["variables"]
    assert "title" in res["variables"]


def test_query4_sections_instructors_semesters(sparql_service):
    """Query 4: Course sections with instructors and semesters must return 40 rows."""
    q_text = sparql_service.get_query_by_id("q4_sections_instructors_semesters")
    assert q_text is not None
    res = sparql_service.execute_query(q_text)
    assert res["success"] is True
    assert res["count"] == 40
    assert "section" in res["variables"]
    assert "instructorName" in res["variables"]


def test_query5_enrollments_students_sections(sparql_service):
    """Query 5: Enrollments linking students to sections must return 1000 rows."""
    q_text = sparql_service.get_query_by_id("q5_enrollments_students_sections")
    assert q_text is not None
    res = sparql_service.execute_query(q_text)
    assert res["success"] is True
    assert res["count"] == 1000
    assert "studentName" in res["variables"]
    assert "letterGrade" in res["variables"]


def test_query6_department_course_counts(sparql_service):
    """Query 6: Aggregate course counts per department must return 14 rows."""
    q_text = sparql_service.get_query_by_id("q6_department_course_counts")
    assert q_text is not None
    res = sparql_service.execute_query(q_text)
    assert res["success"] is True
    assert res["count"] == 14
    assert "courseCount" in res["variables"]


def test_query7_advisor_advisees(sparql_service):
    """Query 7: Advisor-advisees must return 50 rows."""
    q_text = sparql_service.get_query_by_id("q7_advisor_advisees")
    assert q_text is not None
    res = sparql_service.execute_query(q_text)
    assert res["success"] is True
    assert res["count"] == 50
