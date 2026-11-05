"""
UniGraph CSV to RDF Converter
Transforms tabular university data into RDF triples conforming to UniGraph RDFS and FOAF.
Preserves source IDs for complete traceability back to the relational dataset.
"""
import pandas as pd
from pathlib import Path
from rdflib import Graph, Literal, URIRef, RDF, RDFS, XSD, FOAF
from src.config import (
    DATA_DIR,
    RAW_GRAPH_FILE,
    UNIGRAPH,
    DATA,
    bind_prefixes,
)
from src.ontology import build_ontology


def load_csv(filename: str) -> pd.DataFrame:
    """Helper to load a CSV file from data directory."""
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Dataset CSV not found at {path}")
    return pd.read_csv(path)


def convert_csv_to_rdf(save_to_file: bool = True) -> Graph:
    """
    Reads the CSV files, builds RDF triples, and saves data/unigraph.ttl.
    Includes the RDFS ontology schema in the graph.
    """
    g = Graph()
    bind_prefixes(g)

    # 1. Include ontology definition
    onto = build_ontology()
    for s, p, o in onto:
        g.add((s, p, o))

    # 2. Departments
    dept_df = load_csv("departments.csv")
    for _, row in dept_df.iterrows():
        dept_id = int(row["id"])
        dept_uri = DATA[f"department/{dept_id}"]
        g.add((dept_uri, RDF.type, UNIGRAPH.Department))
        g.add((dept_uri, UNIGRAPH.sourceId, Literal(str(dept_id), datatype=XSD.string)))
        if pd.notna(row.get("name")):
            g.add((dept_uri, FOAF.name, Literal(str(row["name"]).strip())))
            g.add((dept_uri, RDFS.label, Literal(str(row["name"]).strip())))
        if pd.notna(row.get("code")):
            g.add((dept_uri, UNIGRAPH.code, Literal(str(row["code"]).strip(), datatype=XSD.string)))
        if pd.notna(row.get("budget")):
            g.add((dept_uri, UNIGRAPH.budget, Literal(float(row["budget"]), datatype=XSD.decimal)))
        if pd.notna(row.get("office_room_id")):
            room_uri = DATA[f"room/{int(row['office_room_id'])}"]
            g.add((dept_uri, UNIGRAPH.hasOfficeRoom, room_uri))

    # 3. Programs
    prog_df = load_csv("programs.csv")
    for _, row in prog_df.iterrows():
        prog_id = int(row["id"])
        prog_uri = DATA[f"program/{prog_id}"]
        g.add((prog_uri, RDF.type, UNIGRAPH.Program))
        g.add((prog_uri, UNIGRAPH.sourceId, Literal(str(prog_id), datatype=XSD.string)))
        if pd.notna(row.get("name")):
            g.add((prog_uri, RDFS.label, Literal(str(row["name"]).strip())))
            g.add((prog_uri, FOAF.name, Literal(str(row["name"]).strip())))
        if pd.notna(row.get("degree_level")):
            g.add((prog_uri, UNIGRAPH.degreeLevel, Literal(str(row["degree_level"]).strip())))
        if pd.notna(row.get("credits_required")):
            g.add((prog_uri, UNIGRAPH.creditsRequired, Literal(int(row["credits_required"]), datatype=XSD.integer)))
        if pd.notna(row.get("department_id")):
            dept_uri = DATA[f"department/{int(row['department_id'])}"]
            g.add((prog_uri, UNIGRAPH.programOfDepartment, dept_uri))
            g.add((dept_uri, UNIGRAPH.offersProgram, prog_uri))

    # 4. Courses
    courses_df = load_csv("courses.csv")
    for _, row in courses_df.iterrows():
        course_id = int(row["id"])
        course_uri = DATA[f"course/{course_id}"]
        g.add((course_uri, RDF.type, UNIGRAPH.Course))
        g.add((course_uri, UNIGRAPH.sourceId, Literal(str(course_id), datatype=XSD.string)))
        if pd.notna(row.get("title")):
            g.add((course_uri, RDFS.label, Literal(str(row["title"]).strip())))
            g.add((course_uri, FOAF.name, Literal(str(row["title"]).strip())))
        if pd.notna(row.get("code")):
            g.add((course_uri, UNIGRAPH.code, Literal(str(row["code"]).strip(), datatype=XSD.string)))
        if pd.notna(row.get("credits")):
            g.add((course_uri, UNIGRAPH.credits, Literal(int(row["credits"]), datatype=XSD.integer)))
        if pd.notna(row.get("description")):
            g.add((course_uri, RDFS.comment, Literal(str(row["description"]).strip())))
        if pd.notna(row.get("department_id")):
            dept_uri = DATA[f"department/{int(row['department_id'])}"]
            g.add((course_uri, UNIGRAPH.courseOfDepartment, dept_uri))
            g.add((dept_uri, UNIGRAPH.offersCourse, course_uri))

    # 5. Course Prerequisites
    prereq_df = load_csv("course_prerequisites.csv")
    for _, row in prereq_df.iterrows():
        if pd.notna(row.get("course_id")) and pd.notna(row.get("prerequisite_course_id")):
            c_uri = DATA[f"course/{int(row['course_id'])}"]
            p_uri = DATA[f"course/{int(row['prerequisite_course_id'])}"]
            g.add((c_uri, UNIGRAPH.hasPrerequisite, p_uri))

    # 6. Buildings & Rooms
    build_df = load_csv("buildings.csv")
    for _, row in build_df.iterrows():
        b_id = int(row["id"])
        b_uri = DATA[f"building/{b_id}"]
        g.add((b_uri, RDF.type, UNIGRAPH.Building))
        g.add((b_uri, UNIGRAPH.sourceId, Literal(str(b_id), datatype=XSD.string)))
        if pd.notna(row.get("name")):
            g.add((b_uri, RDFS.label, Literal(str(row["name"]).strip())))
        if pd.notna(row.get("code")):
            g.add((b_uri, UNIGRAPH.code, Literal(str(row["code"]).strip(), datatype=XSD.string)))

    rooms_df = load_csv("rooms.csv")
    for _, row in rooms_df.iterrows():
        r_id = int(row["id"])
        r_uri = DATA[f"room/{r_id}"]
        g.add((r_uri, RDF.type, UNIGRAPH.Room))
        g.add((r_uri, UNIGRAPH.sourceId, Literal(str(r_id), datatype=XSD.string)))
        if pd.notna(row.get("number")):
            g.add((r_uri, RDFS.label, Literal(f"Room {row['number']}")))
        if pd.notna(row.get("capacity")):
            g.add((r_uri, UNIGRAPH.capacity, Literal(int(row["capacity"]), datatype=XSD.integer)))
        if pd.notna(row.get("building_id")):
            b_uri = DATA[f"building/{int(row['building_id'])}"]
            g.add((r_uri, UNIGRAPH.inBuilding, b_uri))

    # 7. Semesters
    sem_df = load_csv("semesters.csv")
    for _, row in sem_df.iterrows():
        s_id = int(row["id"])
        s_uri = DATA[f"semester/{s_id}"]
        g.add((s_uri, RDF.type, UNIGRAPH.Semester))
        g.add((s_uri, UNIGRAPH.sourceId, Literal(str(s_id), datatype=XSD.string)))
        season = str(row.get("season", "")).strip().capitalize()
        year = int(row.get("year", 0))
        g.add((s_uri, RDFS.label, Literal(f"{season} {year}")))
        g.add((s_uri, UNIGRAPH.season, Literal(str(row.get("season", "")).strip())))
        g.add((s_uri, UNIGRAPH.year, Literal(year, datatype=XSD.integer)))
        if pd.notna(row.get("start_date")):
            g.add((s_uri, UNIGRAPH.startDate, Literal(str(row["start_date"]).strip(), datatype=XSD.date)))
        if pd.notna(row.get("end_date")):
            g.add((s_uri, UNIGRAPH.endDate, Literal(str(row["end_date"]).strip(), datatype=XSD.date)))

    # 8. People (pre-indexed for fast lookup)
    people_df = load_csv("people.csv").set_index("id")

    # 9. Instructors
    # Only assert unigraph:Instructor (or specific subClass Professor/Lecturer) in raw graph.
    # Notice: unigraph:Person and foaf:Person are NOT asserted in the raw graph!
    # They will be inferred via rule rdfs9!
    inst_df = load_csv("instructors.csv")
    for _, row in inst_df.iterrows():
        inst_id = int(row["id"])
        inst_uri = DATA[f"instructor/{inst_id}"]
        rank_val = str(row.get("rank", "")).strip().lower()

        # Specific class assertion: Professor or Lecturer
        if "professor" in rank_val:
            g.add((inst_uri, RDF.type, UNIGRAPH.Professor))
        elif "lecturer" in rank_val:
            g.add((inst_uri, RDF.type, UNIGRAPH.Lecturer))
        else:
            g.add((inst_uri, RDF.type, UNIGRAPH.Instructor))

        g.add((inst_uri, UNIGRAPH.sourceId, Literal(str(inst_id), datatype=XSD.string)))
        if pd.notna(row.get("rank")):
            g.add((inst_uri, UNIGRAPH.rank, Literal(str(row["rank"]).strip())))
        if pd.notna(row.get("salary")):
            g.add((inst_uri, UNIGRAPH.salary, Literal(float(row["salary"]), datatype=XSD.decimal)))
        if pd.notna(row.get("department_id")):
            dept_uri = DATA[f"department/{int(row['department_id'])}"]
            g.add((inst_uri, UNIGRAPH.belongsToDepartment, dept_uri))

        # Person details
        p_id = int(row["person_id"])
        g.add((inst_uri, UNIGRAPH.sourcePersonId, Literal(str(p_id), datatype=XSD.string)))
        if p_id in people_df.index:
            p_row = people_df.loc[p_id]
            fn = str(p_row.get("first_name", "")).strip()
            ln = str(p_row.get("last_name", "")).strip()
            full_name = f"{fn} {ln}".strip()
            if fn:
                g.add((inst_uri, FOAF.firstName, Literal(fn)))
            if ln:
                g.add((inst_uri, FOAF.lastName, Literal(ln)))
            if full_name:
                g.add((inst_uri, FOAF.name, Literal(full_name)))
                g.add((inst_uri, RDFS.label, Literal(full_name)))
            email = str(p_row.get("email", "")).strip()
            if email and email != "nan":
                g.add((inst_uri, FOAF.mbox, URIRef(f"mailto:{email}")))

    # 10. Students
    # Only assert unigraph:Student in raw graph.
    # unigraph:Person and foaf:Person will be inferred via rule rdfs9.
    stud_df = load_csv("students.csv")
    for _, row in stud_df.iterrows():
        stud_id = int(row["id"])
        stud_uri = DATA[f"student/{stud_id}"]
        g.add((stud_uri, RDF.type, UNIGRAPH.Student))
        g.add((stud_uri, UNIGRAPH.sourceId, Literal(str(stud_id), datatype=XSD.string)))

        if pd.notna(row.get("status")):
            g.add((stud_uri, UNIGRAPH.status, Literal(str(row["status"]).strip())))
        if pd.notna(row.get("program_id")):
            prog_uri = DATA[f"program/{int(row['program_id'])}"]
            g.add((stud_uri, UNIGRAPH.enrolledInProgram, prog_uri))

        # Academic Advisor relationship:
        # We assert ONLY unigraph:advises in raw graph!
        # unigraph:supervises will be inferred via rule rdfs7!
        if pd.notna(row.get("advisor_instructor_id")):
            inst_uri = DATA[f"instructor/{int(row['advisor_instructor_id'])}"]
            g.add((inst_uri, UNIGRAPH.advises, stud_uri))

        p_id = int(row["person_id"])
        g.add((stud_uri, UNIGRAPH.sourcePersonId, Literal(str(p_id), datatype=XSD.string)))
        if p_id in people_df.index:
            p_row = people_df.loc[p_id]
            fn = str(p_row.get("first_name", "")).strip()
            ln = str(p_row.get("last_name", "")).strip()
            full_name = f"{fn} {ln}".strip()
            if fn:
                g.add((stud_uri, FOAF.firstName, Literal(fn)))
            if ln:
                g.add((stud_uri, FOAF.lastName, Literal(ln)))
            if full_name:
                g.add((stud_uri, FOAF.name, Literal(full_name)))
                g.add((stud_uri, RDFS.label, Literal(full_name)))
            email = str(p_row.get("email", "")).strip()
            if email and email != "nan":
                g.add((stud_uri, FOAF.mbox, URIRef(f"mailto:{email}")))

    # 11. Sections
    sec_df = load_csv("sections.csv")
    for _, row in sec_df.iterrows():
        sec_id = int(row["id"])
        sec_uri = DATA[f"section/{sec_id}"]
        g.add((sec_uri, RDF.type, UNIGRAPH.CourseSection))
        g.add((sec_uri, UNIGRAPH.sourceId, Literal(str(sec_id), datatype=XSD.string)))

        if pd.notna(row.get("number")):
            sec_num = int(row["number"])
            g.add((sec_uri, UNIGRAPH.sectionNumber, Literal(sec_num, datatype=XSD.integer)))
            g.add((sec_uri, RDFS.label, Literal(f"Section {sec_num} (ID {sec_id})")))
        if pd.notna(row.get("capacity")):
            g.add((sec_uri, UNIGRAPH.capacity, Literal(int(row["capacity"]), datatype=XSD.integer)))
        if pd.notna(row.get("course_id")):
            c_uri = DATA[f"course/{int(row['course_id'])}"]
            g.add((sec_uri, UNIGRAPH.sectionOfCourse, c_uri))
        if pd.notna(row.get("instructor_id")):
            inst_uri = DATA[f"instructor/{int(row['instructor_id'])}"]
            g.add((sec_uri, UNIGRAPH.taughtBy, inst_uri))
        if pd.notna(row.get("semester_id")):
            sem_uri = DATA[f"semester/{int(row['semester_id'])}"]
            g.add((sec_uri, UNIGRAPH.heldInSemester, sem_uri))
        if pd.notna(row.get("room_id")):
            r_uri = DATA[f"room/{int(row['room_id'])}"]
            g.add((sec_uri, UNIGRAPH.heldInRoom, r_uri))

    # 12. Enrollments
    # Only assert enrolledInSection and enrollment details in raw graph.
    # involvedInCourse will be inferred via rule rdfs7!
    enr_df = load_csv("enrollments.csv")
    for _, row in enr_df.iterrows():
        enr_id = int(row["id"])
        enr_uri = DATA[f"enrollment/{enr_id}"]
        g.add((enr_uri, RDF.type, UNIGRAPH.Enrollment))
        g.add((enr_uri, UNIGRAPH.sourceId, Literal(str(enr_id), datatype=XSD.string)))

        stud_uri = DATA[f"student/{int(row['student_id'])}"]
        sec_uri = DATA[f"section/{int(row['section_id'])}"]
        g.add((enr_uri, UNIGRAPH.enrollmentStudent, stud_uri))
        g.add((enr_uri, UNIGRAPH.enrollmentSection, sec_uri))

        # Direct link
        g.add((stud_uri, UNIGRAPH.enrolledInSection, sec_uri))

        if pd.notna(row.get("letter_grade")):
            g.add((enr_uri, UNIGRAPH.letterGrade, Literal(str(row["letter_grade"]).strip())))
        if pd.notna(row.get("grade_points")):
            g.add((enr_uri, UNIGRAPH.gradePoints, Literal(float(row["grade_points"]), datatype=XSD.decimal)))

    if save_to_file:
        RAW_GRAPH_FILE.parent.mkdir(parents=True, exist_ok=True)
        g.serialize(destination=str(RAW_GRAPH_FILE), format="turtle")

    return g


if __name__ == "__main__":
    print("Converting CSV dataset into RDF knowledge graph...")
    g = convert_csv_to_rdf(save_to_file=True)
    print(f"Conversion complete! Saved to {RAW_GRAPH_FILE} ({len(g)} triples).")
