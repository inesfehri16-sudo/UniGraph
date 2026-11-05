"""
UniGraph RDFS Ontology Definition
Defines classes, properties, class hierarchy, property hierarchy, domains, and ranges.
Reuses W3C FOAF (Friend of a Friend) vocabulary for people and organizations.
"""
from rdflib import Graph, Literal, RDF, RDFS, XSD, FOAF
from src.config import UNIGRAPH, bind_prefixes, ONTOLOGY_FILE


def build_ontology() -> Graph:
    """
    Constructs and returns the UniGraph RDFS ontology graph.
    """
    g = Graph()
    bind_prefixes(g)

    # =========================================================================
    # 1. Classes
    # =========================================================================
    classes = [
        # Academic people hierarchy
        (UNIGRAPH.Person, "Person", "A human being within the university system, specialization of foaf:Person."),
        (UNIGRAPH.Student, "Student", "An enrolled student in an academic program."),
        (UNIGRAPH.Instructor, "Instructor", "A member of the academic teaching staff."),
        (UNIGRAPH.Professor, "Professor", "A tenured or tenure-track professor rank (assistant, associate, full)."),
        (UNIGRAPH.Lecturer, "Lecturer", "A teaching instructor with lecturer rank."),
        # University entities
        (UNIGRAPH.Department, "Department", "An academic department within the university, specialization of foaf:Organization."),
        (UNIGRAPH.Program, "Program", "A degree-granting academic curriculum/program."),
        (UNIGRAPH.Course, "Course", "An academic course offered by a department."),
        (UNIGRAPH.CourseSection, "CourseSection", "A specific offering or section of a course during a semester."),
        (UNIGRAPH.Semester, "Semester", "An academic period (e.g. Fall 2021, Spring 2022)."),
        (UNIGRAPH.Enrollment, "Enrollment", "A student's enrollment record in a course section including grade."),
        (UNIGRAPH.Room, "Room", "A physical room where sections are held or offices are located."),
        (UNIGRAPH.Building, "Building", "A campus building containing rooms."),
    ]

    for uri, label, comment in classes:
        g.add((uri, RDF.type, RDFS.Class))
        g.add((uri, RDFS.label, Literal(label, lang="en")))
        g.add((uri, RDFS.comment, Literal(comment, lang="en")))

    # Class Hierarchies (rdfs:subClassOf)
    # Person hierarchy: foaf:Person <- unigraph:Person <- unigraph:Student / unigraph:Instructor
    g.add((UNIGRAPH.Person, RDFS.subClassOf, FOAF.Person))
    g.add((UNIGRAPH.Student, RDFS.subClassOf, UNIGRAPH.Person))
    g.add((UNIGRAPH.Instructor, RDFS.subClassOf, UNIGRAPH.Person))
    g.add((UNIGRAPH.Professor, RDFS.subClassOf, UNIGRAPH.Instructor))
    g.add((UNIGRAPH.Lecturer, RDFS.subClassOf, UNIGRAPH.Instructor))

    # Organization hierarchy: foaf:Organization <- unigraph:Department
    g.add((UNIGRAPH.Department, RDFS.subClassOf, FOAF.Organization))

    # =========================================================================
    # 2. Object Properties
    # =========================================================================
    object_properties = [
        # (URI, Label, Comment, Domain, Range, SubPropertyOf)
        (
            UNIGRAPH.associatedWith,
            "associatedWith",
            "Generic association between a university person and a resource.",
            UNIGRAPH.Person,
            RDFS.Resource,
            None
        ),
        (
            UNIGRAPH.supervises,
            "supervises",
            "Supervisory relationship between an academic staff member and a student.",
            UNIGRAPH.Instructor,
            UNIGRAPH.Student,
            UNIGRAPH.associatedWith
        ),
        (
            UNIGRAPH.advises,
            "advises",
            "Academic advisory relationship: an instructor advises a student.",
            UNIGRAPH.Instructor,
            UNIGRAPH.Student,
            UNIGRAPH.supervises
        ),
        (
            UNIGRAPH.belongsToDepartment,
            "belongsToDepartment",
            "The department an instructor is affiliated with.",
            UNIGRAPH.Instructor,
            UNIGRAPH.Department,
            UNIGRAPH.associatedWith
        ),
        (
            UNIGRAPH.enrolledInProgram,
            "enrolledInProgram",
            "The academic program in which a student is enrolled.",
            UNIGRAPH.Student,
            UNIGRAPH.Program,
            None
        ),
        (
            UNIGRAPH.offersProgram,
            "offersProgram",
            "The academic program offered by a department.",
            UNIGRAPH.Department,
            UNIGRAPH.Program,
            None
        ),
        (
            UNIGRAPH.programOfDepartment,
            "programOfDepartment",
            "The academic department that administers this program.",
            UNIGRAPH.Program,
            UNIGRAPH.Department,
            None
        ),
        (
            UNIGRAPH.offersCourse,
            "offersCourse",
            "A course offered by a department.",
            UNIGRAPH.Department,
            UNIGRAPH.Course,
            None
        ),
        (
            UNIGRAPH.courseOfDepartment,
            "courseOfDepartment",
            "The department that administers this course.",
            UNIGRAPH.Course,
            UNIGRAPH.Department,
            None
        ),
        (
            UNIGRAPH.sectionOfCourse,
            "sectionOfCourse",
            "The parent course to which this section belongs.",
            UNIGRAPH.CourseSection,
            UNIGRAPH.Course,
            None
        ),
        (
            UNIGRAPH.taughtBy,
            "taughtBy",
            "The instructor assigned to teach this course section.",
            UNIGRAPH.CourseSection,
            UNIGRAPH.Instructor,
            None
        ),
        (
            UNIGRAPH.heldInSemester,
            "heldInSemester",
            "The semester in which this course section takes place.",
            UNIGRAPH.CourseSection,
            UNIGRAPH.Semester,
            None
        ),
        (
            UNIGRAPH.heldInRoom,
            "heldInRoom",
            "The room where a course section meets.",
            UNIGRAPH.CourseSection,
            UNIGRAPH.Room,
            None
        ),
        (
            UNIGRAPH.hasOfficeRoom,
            "hasOfficeRoom",
            "The office room allocated to an academic department.",
            UNIGRAPH.Department,
            UNIGRAPH.Room,
            None
        ),
        (
            UNIGRAPH.inBuilding,
            "inBuilding",
            "The building in which a room is situated.",
            UNIGRAPH.Room,
            UNIGRAPH.Building,
            None
        ),
        (
            UNIGRAPH.enrollmentStudent,
            "enrollmentStudent",
            "The student linked to an enrollment record.",
            UNIGRAPH.Enrollment,
            UNIGRAPH.Student,
            None
        ),
        (
            UNIGRAPH.enrollmentSection,
            "enrollmentSection",
            "The course section linked to an enrollment record.",
            UNIGRAPH.Enrollment,
            UNIGRAPH.CourseSection,
            None
        ),
        (
            UNIGRAPH.involvedInCourse,
            "involvedInCourse",
            "Generic involvement of a person in a course or section.",
            UNIGRAPH.Person,
            RDFS.Resource,
            None
        ),
        (
            UNIGRAPH.enrolledInSection,
            "enrolledInSection",
            "Shortcut relation stating a student is enrolled in a course section.",
            UNIGRAPH.Student,
            UNIGRAPH.CourseSection,
            UNIGRAPH.involvedInCourse
        ),
        (
            UNIGRAPH.hasPrerequisite,
            "hasPrerequisite",
            "Prerequisite course required before taking this course.",
            UNIGRAPH.Course,
            UNIGRAPH.Course,
            None
        ),
    ]

    for uri, label, comment, domain, rng, sub_prop in object_properties:
        g.add((uri, RDF.type, RDF.Property))
        g.add((uri, RDFS.label, Literal(label, lang="en")))
        g.add((uri, RDFS.comment, Literal(comment, lang="en")))
        if domain:
            g.add((uri, RDFS.domain, domain))
        if rng:
            g.add((uri, RDFS.range, rng))
        if sub_prop:
            g.add((uri, RDFS.subPropertyOf, sub_prop))

    # =========================================================================
    # 3. Datatype Properties
    # =========================================================================
    datatype_properties = [
        (UNIGRAPH.sourceId, "sourceId", "Traceability identifier preserved from the original CSV dataset.", RDFS.Resource, XSD.string),
        (UNIGRAPH.sourcePersonId, "sourcePersonId", "Traceability identifier of person record from people.csv.", UNIGRAPH.Person, XSD.string),
        (UNIGRAPH.code, "code", "Official university identifier code (department or course).", RDFS.Resource, XSD.string),
        (UNIGRAPH.credits, "credits", "Number of academic credit hours for a course.", UNIGRAPH.Course, XSD.integer),
        (UNIGRAPH.creditsRequired, "creditsRequired", "Total credits required for a degree program.", UNIGRAPH.Program, XSD.integer),
        (UNIGRAPH.degreeLevel, "degreeLevel", "Level of academic degree (e.g. bachelor, master, phd).", UNIGRAPH.Program, XSD.string),
        (UNIGRAPH.status, "status", "Academic standing/status of a student (e.g. active, graduated).", UNIGRAPH.Student, XSD.string),
        (UNIGRAPH.rank, "rank", "Academic faculty rank (e.g. professor, assistant_professor).", UNIGRAPH.Instructor, XSD.string),
        (UNIGRAPH.salary, "salary", "Annual salary of academic staff member.", UNIGRAPH.Instructor, XSD.decimal),
        (UNIGRAPH.letterGrade, "letterGrade", "Letter grade awarded in an enrollment (e.g. A, B+, C).", UNIGRAPH.Enrollment, XSD.string),
        (UNIGRAPH.gradePoints, "gradePoints", "Numerical grade points earned in an enrollment.", UNIGRAPH.Enrollment, XSD.decimal),
        (UNIGRAPH.sectionNumber, "sectionNumber", "Section sequence number of a course offering.", UNIGRAPH.CourseSection, XSD.integer),
        (UNIGRAPH.capacity, "capacity", "Maximum seating or enrollment capacity.", RDFS.Resource, XSD.integer),
        (UNIGRAPH.season, "season", "Semester academic season (spring, summer, fall).", UNIGRAPH.Semester, XSD.string),
        (UNIGRAPH.year, "year", "Academic calendar year.", UNIGRAPH.Semester, XSD.integer),
        (UNIGRAPH.startDate, "startDate", "Start date of an academic semester.", UNIGRAPH.Semester, XSD.date),
        (UNIGRAPH.endDate, "endDate", "End date of an academic semester.", UNIGRAPH.Semester, XSD.date),
        (UNIGRAPH.budget, "budget", "Annual financial budget of an academic department.", UNIGRAPH.Department, XSD.decimal),
    ]

    for uri, label, comment, domain, rng in datatype_properties:
        g.add((uri, RDF.type, RDF.Property))
        g.add((uri, RDFS.label, Literal(label, lang="en")))
        g.add((uri, RDFS.comment, Literal(comment, lang="en")))
        if domain:
            g.add((uri, RDFS.domain, domain))
        if rng:
            g.add((uri, RDFS.range, rng))

    return g


def save_ontology(target_path=ONTOLOGY_FILE) -> Graph:
    """Builds and serializes the ontology to Turtle format."""
    g = build_ontology()
    target_path.parent.mkdir(parents=True, exist_ok=True)
    g.serialize(destination=str(target_path), format="turtle")
    return g


if __name__ == "__main__":
    g = save_ontology()
    print(f"Ontology saved to {ONTOLOGY_FILE} ({len(g)} triples).")
