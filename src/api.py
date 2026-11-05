"""
UniGraph REST API
Flask-based RESTful service exposing the University Knowledge Graph,
SPARQL query executor, RDFS inference demonstrations, and ontology metadata.
"""
from flask import Flask, jsonify, request, render_template, send_from_directory, send_file
from pathlib import Path
from typing import Dict, Any
from rdflib import Graph

from src.config import (
    BASE_DIR,
    DATA_DIR,
    ONTOLOGY_DIR,
    RAW_GRAPH_FILE,
    INFERRED_GRAPH_FILE,
    UNIGRAPH,
    DATA,
    FOAF,
    bind_prefixes
)
from src.sparql_service import SPARQLService
from src.inference import get_inference_demonstrations, run_inference
from src.ontology import build_ontology


def create_app(test_config=None) -> Flask:
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static")
    )

    if test_config:
        app.config.update(test_config)

    # Initialize Graph and Services
    raw_graph = Graph()
    bind_prefixes(raw_graph)
    if RAW_GRAPH_FILE.exists():
        raw_graph.parse(str(RAW_GRAPH_FILE), format="turtle")

    inferred_graph = Graph()
    bind_prefixes(inferred_graph)
    if INFERRED_GRAPH_FILE.exists():
        inferred_graph.parse(str(INFERRED_GRAPH_FILE), format="turtle")
    else:
        # Fallback: if inferred graph not yet created, run inference
        inferred_graph, _ = run_inference(raw_graph, save_files=True)

    sparql_raw = SPARQLService(graph=raw_graph, use_inferred=False)
    sparql_inf = SPARQLService(graph=inferred_graph, use_inferred=True)

    # CORS support
    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
        return response

    # Web Dashboard Route
    @app.route("/", methods=["GET"])
    def index():
        return render_template("index.html")

    # 1. Health / Status Check Endpoint
    @app.route("/api/status", methods=["GET"])
    def get_status():
        """Returns API health status, graph metrics, and entity counts."""
        try:
            status_data = {
                "status": "healthy",
                "service": "UniGraph REST API",
                "version": "1.0.0",
                "graph_statistics": {
                    "raw_triples": len(raw_graph),
                    "inferred_triples_total": len(inferred_graph),
                    "newly_inferred_triples": len(inferred_graph) - len(raw_graph)
                },
                "entity_counts": {
                    "students": len(list(raw_graph.subjects(predicate=None, object=UNIGRAPH.Student))),
                    "instructors": len(list(raw_graph.triples((None, UNIGRAPH.belongsToDepartment, None)))),
                    "departments": len(list(raw_graph.subjects(predicate=None, object=UNIGRAPH.Department))),
                    "programs": len(list(raw_graph.subjects(predicate=None, object=UNIGRAPH.Program))),
                    "courses": len(list(raw_graph.subjects(predicate=None, object=UNIGRAPH.Course))),
                    "sections": len(list(raw_graph.subjects(predicate=None, object=UNIGRAPH.CourseSection))),
                    "enrollments": len(list(raw_graph.subjects(predicate=None, object=UNIGRAPH.Enrollment)))
                }
            }
            return jsonify({"success": True, "data": status_data}), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    # 2. Ontology & Schema Information Endpoint
    @app.route("/api/ontology", methods=["GET"])
    def get_ontology_info():
        """Returns classes, properties, subClassOf, subPropertyOf, domains, and ranges."""
        try:
            classes_info = [
                {"uri": str(UNIGRAPH.Person), "label": "Person", "subClassOf": "foaf:Person"},
                {"uri": str(UNIGRAPH.Student), "label": "Student", "subClassOf": "unigraph:Person"},
                {"uri": str(UNIGRAPH.Instructor), "label": "Instructor", "subClassOf": "unigraph:Person"},
                {"uri": str(UNIGRAPH.Professor), "label": "Professor", "subClassOf": "unigraph:Instructor"},
                {"uri": str(UNIGRAPH.Lecturer), "label": "Lecturer", "subClassOf": "unigraph:Instructor"},
                {"uri": str(UNIGRAPH.Department), "label": "Department", "subClassOf": "foaf:Organization"},
                {"uri": str(UNIGRAPH.Program), "label": "Program", "subClassOf": None},
                {"uri": str(UNIGRAPH.Course), "label": "Course", "subClassOf": None},
                {"uri": str(UNIGRAPH.CourseSection), "label": "CourseSection", "subClassOf": None},
                {"uri": str(UNIGRAPH.Semester), "label": "Semester", "subClassOf": None},
                {"uri": str(UNIGRAPH.Enrollment), "label": "Enrollment", "subClassOf": None},
                {"uri": str(UNIGRAPH.Room), "label": "Room", "subClassOf": None},
                {"uri": str(UNIGRAPH.Building), "label": "Building", "subClassOf": None},
            ]

            properties_info = [
                {"uri": str(UNIGRAPH.advises), "label": "advises", "domain": "Instructor", "range": "Student", "subPropertyOf": "supervises"},
                {"uri": str(UNIGRAPH.supervises), "label": "supervises", "domain": "Instructor", "range": "Student", "subPropertyOf": "associatedWith"},
                {"uri": str(UNIGRAPH.belongsToDepartment), "label": "belongsToDepartment", "domain": "Instructor", "range": "Department", "subPropertyOf": "associatedWith"},
                {"uri": str(UNIGRAPH.enrolledInProgram), "label": "enrolledInProgram", "domain": "Student", "range": "Program", "subPropertyOf": None},
                {"uri": str(UNIGRAPH.offersCourse), "label": "offersCourse", "domain": "Department", "range": "Course", "subPropertyOf": None},
                {"uri": str(UNIGRAPH.courseOfDepartment), "label": "courseOfDepartment", "domain": "Course", "range": "Department", "subPropertyOf": None},
                {"uri": str(UNIGRAPH.offersProgram), "label": "offersProgram", "domain": "Department", "range": "Program", "subPropertyOf": None},
                {"uri": str(UNIGRAPH.sectionOfCourse), "label": "sectionOfCourse", "domain": "CourseSection", "range": "Course", "subPropertyOf": None},
                {"uri": str(UNIGRAPH.taughtBy), "label": "taughtBy", "domain": "CourseSection", "range": "Instructor", "subPropertyOf": None},
                {"uri": str(UNIGRAPH.heldInSemester), "label": "heldInSemester", "domain": "CourseSection", "range": "Semester", "subPropertyOf": None},
                {"uri": str(UNIGRAPH.enrollmentStudent), "label": "enrollmentStudent", "domain": "Enrollment", "range": "Student", "subPropertyOf": None},
                {"uri": str(UNIGRAPH.enrollmentSection), "label": "enrollmentSection", "domain": "Enrollment", "range": "CourseSection", "subPropertyOf": None},
                {"uri": str(UNIGRAPH.enrolledInSection), "label": "enrolledInSection", "domain": "Student", "range": "CourseSection", "subPropertyOf": "involvedInCourse"},
                {"uri": str(UNIGRAPH.hasPrerequisite), "label": "hasPrerequisite", "domain": "Course", "range": "Course", "subPropertyOf": None},
            ]

            return jsonify({
                "success": True,
                "data": {
                    "namespace": str(UNIGRAPH),
                    "reused_vocabularies": ["FOAF (http://xmlns.com/foaf/0.1/)", "RDFS", "XSD"],
                    "classes_count": len(classes_info),
                    "classes": classes_info,
                    "properties_count": len(properties_info),
                    "properties": properties_info
                }
            }), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    # 3. Students and Programs Endpoint
    @app.route("/api/students", methods=["GET"])
    def get_students():
        """Lists students with program, advisor, and status. Supports ?status=... and ?limit=..."""
        status_filter = request.args.get("status")
        limit = request.args.get("limit", default=50, type=int)

        query = """
        PREFIX unigraph: <https://unigraph.org/schema#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?student ?studentName ?email ?programName ?degreeLevel ?status ?advisorName
        WHERE {
            ?student a unigraph:Student ;
                     foaf:name ?studentName ;
                     unigraph:enrolledInProgram ?program .
            OPTIONAL { ?student foaf:mbox ?mbox . BIND(STRAFTER(STR(?mbox), "mailto:") AS ?email) }
            OPTIONAL { ?student unigraph:status ?status }
            OPTIONAL { ?program rdfs:label ?programName }
            OPTIONAL { ?program unigraph:degreeLevel ?degreeLevel }
            OPTIONAL {
                ?advisor unigraph:advises ?student ;
                         foaf:name ?advisorName .
            }
        """
        if status_filter:
            query += f' FILTER(LCASE(STR(?status)) = "{status_filter.lower()}") '
        query += f"""
        }}
        ORDER BY ?studentName
        LIMIT {limit}
        """

        res = sparql_raw.execute_query(query)
        if not res["success"]:
            return jsonify({"success": False, "error": res["error"]}), 500
        return jsonify({"success": True, "count": res["count"], "data": res["results"]}), 200

    # 4. Instructors and Departments Endpoint
    @app.route("/api/instructors", methods=["GET"])
    def get_instructors():
        """Lists instructors with department, rank, and salary."""
        dept_filter = request.args.get("department")
        rank_filter = request.args.get("rank")

        query = """
        PREFIX unigraph: <https://unigraph.org/schema#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>

        SELECT ?instructor ?instructorName ?email ?rank ?salary ?departmentName ?departmentCode
        WHERE {
            ?instructor unigraph:belongsToDepartment ?department ;
                        foaf:name ?instructorName .
            OPTIONAL { ?instructor foaf:mbox ?mbox . BIND(STRAFTER(STR(?mbox), "mailto:") AS ?email) }
            OPTIONAL { ?instructor unigraph:rank ?rank }
            OPTIONAL { ?instructor unigraph:salary ?salary }
            OPTIONAL { ?department foaf:name ?departmentName }
            OPTIONAL { ?department unigraph:code ?departmentCode }
        """
        if dept_filter:
            query += f' FILTER(CONTAINS(LCASE(STR(?departmentName)), "{dept_filter.lower()}")) '
        if rank_filter:
            query += f' FILTER(LCASE(STR(?rank)) = "{rank_filter.lower()}") '
        query += """
        }
        ORDER BY ?departmentName ?instructorName
        """

        res = sparql_raw.execute_query(query)
        if not res["success"]:
            return jsonify({"success": False, "error": res["error"]}), 500
        return jsonify({"success": True, "count": res["count"], "data": res["results"]}), 200

    # 5. Courses and Course Sections Endpoint
    @app.route("/api/courses", methods=["GET"])
    def get_courses():
        """Lists courses with offering departments and credits. Supports ?limit=... and ?department=..."""
        limit = request.args.get("limit", default=50, type=int)
        dept_filter = request.args.get("department")

        query = f"""
        PREFIX unigraph: <https://unigraph.org/schema#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?course ?courseCode ?title ?credits ?departmentName
        WHERE {{
            ?course a unigraph:Course ;
                    unigraph:code ?courseCode ;
                    rdfs:label ?title ;
                    unigraph:courseOfDepartment ?department .
            OPTIONAL {{ ?course unigraph:credits ?credits }}
            OPTIONAL {{ ?department foaf:name ?departmentName }}
        """
        if dept_filter:
            query += f' FILTER(CONTAINS(LCASE(STR(?departmentName)), "{dept_filter.lower()}")) '
        query += f"""
        }}
        ORDER BY ?courseCode
        LIMIT {limit}
        """

        res = sparql_raw.execute_query(query)
        if not res["success"]:
            return jsonify({"success": False, "error": res["error"]}), 500
        return jsonify({"success": True, "count": res["count"], "data": res["results"]}), 200

    # Course Sections Endpoint
    @app.route("/api/sections", methods=["GET"])
    def get_sections():
        """Lists course sections with course, instructor, semester, and room."""
        query = """
        PREFIX unigraph: <https://unigraph.org/schema#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?section ?courseCode ?courseTitle ?sectionNumber ?capacity ?instructorName ?semesterLabel ?roomLabel
        WHERE {
            ?section a unigraph:CourseSection ;
                     unigraph:sectionOfCourse ?course ;
                     unigraph:taughtBy ?instructor ;
                     unigraph:heldInSemester ?semester .
            OPTIONAL { ?section unigraph:sectionNumber ?sectionNumber }
            OPTIONAL { ?section unigraph:capacity ?capacity }
            OPTIONAL { ?course unigraph:code ?courseCode }
            OPTIONAL { ?course rdfs:label ?courseTitle }
            OPTIONAL { ?instructor foaf:name ?instructorName }
            OPTIONAL { ?semester rdfs:label ?semesterLabel }
            OPTIONAL { 
                ?section unigraph:heldInRoom ?room .
                ?room rdfs:label ?roomLabel .
            }
        }
        ORDER BY ?semesterLabel ?courseCode ?sectionNumber
        """
        res = sparql_raw.execute_query(query)
        if not res["success"]:
            return jsonify({"success": False, "error": res["error"]}), 500
        return jsonify({"success": True, "count": res["count"], "data": res["results"]}), 200

    # Enrollments Endpoint
    @app.route("/api/enrollments", methods=["GET"])
    def get_enrollments():
        """Lists student enrollments with grades. Supports ?limit=..."""
        limit = request.args.get("limit", default=50, type=int)
        query = f"""
        PREFIX unigraph: <https://unigraph.org/schema#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?enrollment ?studentName ?courseCode ?courseTitle ?sectionNumber ?letterGrade ?gradePoints
        WHERE {{
            ?enrollment a unigraph:Enrollment ;
                        unigraph:enrollmentStudent ?student ;
                        unigraph:enrollmentSection ?section .
            ?student foaf:name ?studentName .
            ?section unigraph:sectionOfCourse ?course .
            OPTIONAL {{ ?section unigraph:sectionNumber ?sectionNumber }}
            OPTIONAL {{ ?course unigraph:code ?courseCode }}
            OPTIONAL {{ ?course rdfs:label ?courseTitle }}
            OPTIONAL {{ ?enrollment unigraph:letterGrade ?letterGrade }}
            OPTIONAL {{ ?enrollment unigraph:gradePoints ?gradePoints }}
        }}
        ORDER BY ?studentName ?courseCode
        LIMIT {limit}
        """
        res = sparql_raw.execute_query(query)
        if not res["success"]:
            return jsonify({"success": False, "error": res["error"]}), 500
        return jsonify({"success": True, "count": res["count"], "data": res["results"]}), 200

    # 6. SPARQL Queries Listing & Runner
    @app.route("/api/sparql/queries", methods=["GET"])
    def list_queries():
        """Returns the list of all available predefined SPARQL queries."""
        queries = sparql_raw.list_saved_queries()
        return jsonify({"success": True, "count": len(queries), "data": queries}), 200

    @app.route("/api/sparql/execute", methods=["POST"])
    def execute_sparql():
        """
        Executes a SPARQL query.
        Body:
            {
                "query": "SELECT ...",
                "query_id": "q1_students_programs" (optional),
                "use_inferred": true/false (optional, default false)
            }
        """
        data = request.get_json(silent=True) or {}
        query_str = data.get("query")
        query_id = data.get("query_id")
        use_inferred = bool(data.get("use_inferred", False))

        if query_id and not query_str:
            query_str = sparql_raw.get_query_by_id(query_id)
            if not query_str:
                return jsonify({"success": False, "error": f"Predefined query '{query_id}' not found."}), 404

        if not query_str or not str(query_str).strip():
            return jsonify({"success": False, "error": "Query string or valid query_id is required."}), 400

        service = sparql_inf if use_inferred else sparql_raw
        result = service.execute_query(query_str)

        status_code = 200 if result["success"] else 400
        return jsonify(result), status_code

    # 7. RDFS Inference Demonstration Endpoint
    @app.route("/api/inference/demo", methods=["GET"])
    def get_inference_demo():
        """Returns detailed before and after metrics and triples for all RDFS inference demonstrations."""
        try:
            demos = get_inference_demonstrations(raw_g=raw_graph, exp_g=inferred_graph)
            return jsonify({"success": True, "data": demos}), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    # 8. Export Files Endpoint
    @app.route("/api/export/<target>", methods=["GET"])
    def export_graph(target: str):
        """Allows downloading Turtle RDF files: 'raw', 'inferred', 'ontology', or 'inferred_only'."""
        mapping = {
            "raw": RAW_GRAPH_FILE,
            "inferred": INFERRED_GRAPH_FILE,
            "ontology": ONTOLOGY_DIR / "unigraph_ontology.ttl",
            "diagram": ONTOLOGY_DIR / "ontology_diagram.svg",
        }
        if target not in mapping or not mapping[target].exists():
            return jsonify({"success": False, "error": f"Target '{target}' not found."}), 404
        return send_file(mapping[target], as_attachment=False)

    # 404 Error handler
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "error": "Endpoint not found", "status": 404}), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"success": False, "error": "Internal server error", "status": 500}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    print("Starting UniGraph REST API on http://127.0.0.1:5000 ...")
    app.run(host="0.0.0.0", port=5000, debug=False)
