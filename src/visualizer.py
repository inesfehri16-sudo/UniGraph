"""
UniGraph Ontology Visualizer
Generates clean, readable graphical diagrams of the ontology schema:
- SVG (crisp scalable vector graphic)
- PNG (raster image via matplotlib)
- DOT (Graphviz specification)
- Mermaid (Markdown-compatible diagram)
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from src.config import ONTOLOGY_DIR, DOCS_DIR


def generate_mermaid_diagram() -> str:
    """Creates a Mermaid diagram representation of the UniGraph ontology."""
    mmd = """classDiagram
    direction TB
    
    class foaf_Person {
        <<FOAF Vocabulary>>
        +String name
        +String firstName
        +String lastName
        +String mbox
    }
    
    class foaf_Organization {
        <<FOAF Vocabulary>>
        +String name
    }

    class Person {
        <<UniGraph Schema>>
        +String sourceId
    }

    class Student {
        <<UniGraph Schema>>
        +String status
        +Date enrollmentDate
    }

    class Instructor {
        <<UniGraph Schema>>
        +String rank
        +Decimal salary
    }

    class Professor {
        <<UniGraph Schema>>
    }

    class Lecturer {
        <<UniGraph Schema>>
    }

    class Department {
        <<UniGraph Schema>>
        +String code
        +Decimal budget
    }

    class Program {
        <<UniGraph Schema>>
        +String degreeLevel
        +Integer creditsRequired
    }

    class Course {
        <<UniGraph Schema>>
        +String code
        +Integer credits
        +String description
    }

    class CourseSection {
        <<UniGraph Schema>>
        +Integer sectionNumber
        +Integer capacity
    }

    class Semester {
        <<UniGraph Schema>>
        +String season
        +Integer year
        +Date startDate
        +Date endDate
    }

    class Enrollment {
        <<UniGraph Schema>>
        +String letterGrade
        +Decimal gradePoints
    }

    class Room {
        <<UniGraph Schema>>
        +Integer capacity
    }

    class Building {
        <<UniGraph Schema>>
        +String code
    }

    %% Inheritance (rdfs:subClassOf)
    foaf_Person <|-- Person : rdfs:subClassOf
    Person <|-- Student : rdfs:subClassOf
    Person <|-- Instructor : rdfs:subClassOf
    Instructor <|-- Professor : rdfs:subClassOf
    Instructor <|-- Lecturer : rdfs:subClassOf
    foaf_Organization <|-- Department : rdfs:subClassOf

    %% Relationships (Object Properties)
    Instructor --> Student : advises (subPropertyOf supervises)
    Instructor --> Student : supervises
    Instructor --> Department : belongsToDepartment
    Student --> Program : enrolledInProgram
    Department --> Program : offersProgram
    Department --> Course : offersCourse
    Course --> Department : courseOfDepartment
    Course --> Course : hasPrerequisite
    CourseSection --> Course : sectionOfCourse
    CourseSection --> Instructor : taughtBy
    CourseSection --> Semester : heldInSemester
    CourseSection --> Room : heldInRoom
    Enrollment --> Student : enrollmentStudent
    Enrollment --> CourseSection : enrollmentSection
    Student --> CourseSection : enrolledInSection (subPropertyOf involvedInCourse)
    Room --> Building : inBuilding
"""
    return mmd


def generate_dot_diagram() -> str:
    """Creates a Graphviz DOT representation of the UniGraph ontology."""
    dot = """digraph UniGraphOntology {
    rankdir=LR;
    node [shape=box, style="filled,rounded", fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=8];

    // FOAF External Classes
    "foaf:Person" [fillcolor="#E8F0FE", color="#4285F4", penwidth=2];
    "foaf:Organization" [fillcolor="#E8F0FE", color="#4285F4", penwidth=2];

    // UniGraph Classes
    "unigraph:Person" [fillcolor="#E6F4EA", color="#34A853", penwidth=2];
    "unigraph:Student" [fillcolor="#CEEAD6", color="#137333", penwidth=2];
    "unigraph:Instructor" [fillcolor="#CEEAD6", color="#137333", penwidth=2];
    "unigraph:Professor" [fillcolor="#A8DAB5", color="#0D652D", penwidth=2];
    "unigraph:Lecturer" [fillcolor="#A8DAB5", color="#0D652D", penwidth=2];
    "unigraph:Department" [fillcolor="#FEF7E0", color="#FBBC04", penwidth=2];
    "unigraph:Program" [fillcolor="#FEF7E0", color="#F9AB00", penwidth=2];
    "unigraph:Course" [fillcolor="#FCE8E6", color="#EA4335", penwidth=2];
    "unigraph:CourseSection" [fillcolor="#FCE8E6", color="#D93025", penwidth=2];
    "unigraph:Semester" [fillcolor="#F1F3F4", color="#5F6368", penwidth=2];
    "unigraph:Enrollment" [fillcolor="#E8EAED", color="#3C4043", penwidth=2];
    "unigraph:Room" [fillcolor="#F3E8FD", color="#9334E6", penwidth=2];
    "unigraph:Building" [fillcolor="#F3E8FD", color="#7627BB", penwidth=2];

    // SubClassOf (inheritance)
    "unigraph:Person" -> "foaf:Person" [label="rdfs:subClassOf", style=dashed, color="#4285F4", arrowhead=empty];
    "unigraph:Student" -> "unigraph:Person" [label="rdfs:subClassOf", style=dashed, color="#137333", arrowhead=empty];
    "unigraph:Instructor" -> "unigraph:Person" [label="rdfs:subClassOf", style=dashed, color="#137333", arrowhead=empty];
    "unigraph:Professor" -> "unigraph:Instructor" [label="rdfs:subClassOf", style=dashed, color="#0D652D", arrowhead=empty];
    "unigraph:Lecturer" -> "unigraph:Instructor" [label="rdfs:subClassOf", style=dashed, color="#0D652D", arrowhead=empty];
    "unigraph:Department" -> "foaf:Organization" [label="rdfs:subClassOf", style=dashed, color="#4285F4", arrowhead=empty];

    // Object Properties
    "unigraph:Instructor" -> "unigraph:Student" [label="unigraph:advises\n(subPropertyOf: supervises)", color="#137333"];
    "unigraph:Instructor" -> "unigraph:Department" [label="unigraph:belongsToDepartment", color="#137333"];
    "unigraph:Student" -> "unigraph:Program" [label="unigraph:enrolledInProgram", color="#137333"];
    "unigraph:Department" -> "unigraph:Course" [label="unigraph:offersCourse", color="#FBBC04"];
    "unigraph:Department" -> "unigraph:Program" [label="unigraph:offersProgram", color="#FBBC04"];
    "unigraph:Course" -> "unigraph:Course" [label="unigraph:hasPrerequisite", color="#EA4335"];
    "unigraph:CourseSection" -> "unigraph:Course" [label="unigraph:sectionOfCourse", color="#EA4335"];
    "unigraph:CourseSection" -> "unigraph:Instructor" [label="unigraph:taughtBy", color="#EA4335"];
    "unigraph:CourseSection" -> "unigraph:Semester" [label="unigraph:heldInSemester", color="#EA4335"];
    "unigraph:CourseSection" -> "unigraph:Room" [label="unigraph:heldInRoom", color="#EA4335"];
    "unigraph:Enrollment" -> "unigraph:Student" [label="unigraph:enrollmentStudent", color="#5F6368"];
    "unigraph:Enrollment" -> "unigraph:CourseSection" [label="unigraph:enrollmentSection", color="#5F6368"];
    "unigraph:Student" -> "unigraph:CourseSection" [label="unigraph:enrolledInSection", color="#137333"];
    "unigraph:Room" -> "unigraph:Building" [label="unigraph:inBuilding", color="#9334E6"];
}
"""
    return dot


def generate_svg_diagram(output_path: Path) -> None:
    """Generates a responsive, publication-quality standalone SVG diagram."""
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 780" width="100%" height="100%" style="background:#ffffff; font-family:'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#1e293b"/>
    </marker>
    <marker id="arrow-subclass" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <polygon points="0,1 10,5 0,9" fill="#ffffff" stroke="#2563eb" stroke-width="1.5"/>
    </marker>
    <marker id="arrow-green" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#16a34a"/>
    </marker>
    <marker id="arrow-red" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#dc2626"/>
    </marker>
    <filter id="shadow" x="-5%" y="-5%" width="110%" height="115%" filterUnits="userSpaceOnUse">
      <feDropShadow dx="2" dy="3" stdDeviation="3" flood-opacity="0.12"/>
    </filter>
  </defs>

  <!-- Title & Subtitle -->
  <text x="550" y="38" text-anchor="middle" font-size="24" font-weight="bold" fill="#0f172a">UniGraph — Ontology Schema &amp; RDFS Axioms</text>
  <text x="550" y="60" text-anchor="middle" font-size="13" fill="#64748b">W3C RDF/RDFS Conceptual Model with FOAF Vocabulary Reuse &amp; Inference Rules</text>

  <!-- Legend -->
  <g transform="translate(60, 80)">
    <rect width="980" height="40" rx="8" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1"/>
    <rect x="20" y="14" width="16" height="12" rx="3" fill="#e0e7ff" stroke="#4f46e5" stroke-width="1.5"/>
    <text x="44" y="24" font-size="11" fill="#334155">External FOAF Class</text>
    
    <rect x="180" y="14" width="16" height="12" rx="3" fill="#dcfce7" stroke="#16a34a" stroke-width="1.5"/>
    <text x="204" y="24" font-size="11" fill="#334155">UniGraph People &amp; Roles</text>

    <rect x="360" y="14" width="16" height="12" rx="3" fill="#fef3c7" stroke="#d97706" stroke-width="1.5"/>
    <text x="384" y="24" font-size="11" fill="#334155">Academic Structure</text>

    <rect x="520" y="14" width="16" height="12" rx="3" fill="#fee2e2" stroke="#dc2626" stroke-width="1.5"/>
    <text x="544" y="24" font-size="11" fill="#334155">Course Offerings</text>

    <line x1="680" y1="20" x2="710" y2="20" stroke="#2563eb" stroke-width="2" stroke-dasharray="4,3" marker-end="url(#arrow-subclass)"/>
    <text x="718" y="24" font-size="11" fill="#334155">rdfs:subClassOf</text>

    <line x1="820" y1="20" x2="850" y2="20" stroke="#1e293b" stroke-width="2" marker-end="url(#arrow)"/>
    <text x="858" y="24" font-size="11" fill="#334155">Object Property</text>
  </g>

  <!-- External FOAF Classes -->
  <!-- foaf:Person -->
  <g transform="translate(180, 150)" filter="url(#shadow)">
    <rect width="180" height="60" rx="8" fill="#e0e7ff" stroke="#4f46e5" stroke-width="2"/>
    <text x="90" y="26" text-anchor="middle" font-size="14" font-weight="bold" fill="#312e81">&lt;&lt;FOAF&gt;&gt;</text>
    <text x="90" y="46" text-anchor="middle" font-size="15" font-weight="bold" fill="#1e1b4b">foaf:Person</text>
  </g>

  <!-- foaf:Organization -->
  <g transform="translate(750, 150)" filter="url(#shadow)">
    <rect width="180" height="60" rx="8" fill="#e0e7ff" stroke="#4f46e5" stroke-width="2"/>
    <text x="90" y="26" text-anchor="middle" font-size="14" font-weight="bold" fill="#312e81">&lt;&lt;FOAF&gt;&gt;</text>
    <text x="90" y="46" text-anchor="middle" font-size="15" font-weight="bold" fill="#1e1b4b">foaf:Organization</text>
  </g>

  <!-- unigraph:Person -->
  <g transform="translate(180, 260)" filter="url(#shadow)">
    <rect width="180" height="55" rx="8" fill="#f0fdf4" stroke="#16a34a" stroke-width="2"/>
    <text x="90" y="32" text-anchor="middle" font-size="15" font-weight="bold" fill="#14532d">unigraph:Person</text>
  </g>

  <!-- unigraph:Student -->
  <g transform="translate(60, 370)" filter="url(#shadow)">
    <rect width="180" height="75" rx="8" fill="#dcfce7" stroke="#15803d" stroke-width="2"/>
    <text x="90" y="28" text-anchor="middle" font-size="15" font-weight="bold" fill="#14532d">unigraph:Student</text>
    <text x="90" y="48" text-anchor="middle" font-size="11" fill="#166534">status : String</text>
    <text x="90" y="64" text-anchor="middle" font-size="11" fill="#166534">sourceId : String</text>
  </g>

  <!-- unigraph:Instructor -->
  <g transform="translate(300, 370)" filter="url(#shadow)">
    <rect width="180" height="75" rx="8" fill="#dcfce7" stroke="#15803d" stroke-width="2"/>
    <text x="90" y="28" text-anchor="middle" font-size="15" font-weight="bold" fill="#14532d">unigraph:Instructor</text>
    <text x="90" y="48" text-anchor="middle" font-size="11" fill="#166534">rank : String</text>
    <text x="90" y="64" text-anchor="middle" font-size="11" fill="#166534">salary : Decimal</text>
  </g>

  <!-- Subclasses of Instructor: Professor & Lecturer -->
  <g transform="translate(240, 500)" filter="url(#shadow)">
    <rect width="140" height="45" rx="8" fill="#bbf7d0" stroke="#166534" stroke-width="1.5"/>
    <text x="70" y="28" text-anchor="middle" font-size="13" font-weight="bold" fill="#14532d">unigraph:Professor</text>
  </g>
  <g transform="translate(400, 500)" filter="url(#shadow)">
    <rect width="140" height="45" rx="8" fill="#bbf7d0" stroke="#166534" stroke-width="1.5"/>
    <text x="70" y="28" text-anchor="middle" font-size="13" font-weight="bold" fill="#14532d">unigraph:Lecturer</text>
  </g>

  <!-- unigraph:Department -->
  <g transform="translate(750, 260)" filter="url(#shadow)">
    <rect width="180" height="75" rx="8" fill="#fef3c7" stroke="#d97706" stroke-width="2"/>
    <text x="90" y="28" text-anchor="middle" font-size="15" font-weight="bold" fill="#78350f">unigraph:Department</text>
    <text x="90" y="48" text-anchor="middle" font-size="11" fill="#92400e">code : String</text>
    <text x="90" y="64" text-anchor="middle" font-size="11" fill="#92400e">budget : Decimal</text>
  </g>

  <!-- unigraph:Program -->
  <g transform="translate(530, 260)" filter="url(#shadow)">
    <rect width="160" height="75" rx="8" fill="#fef3c7" stroke="#d97706" stroke-width="2"/>
    <text x="80" y="28" text-anchor="middle" font-size="14" font-weight="bold" fill="#78350f">unigraph:Program</text>
    <text x="80" y="48" text-anchor="middle" font-size="11" fill="#92400e">degreeLevel : String</text>
    <text x="80" y="64" text-anchor="middle" font-size="11" fill="#92400e">creditsReq : Int</text>
  </g>

  <!-- unigraph:Course -->
  <g transform="translate(750, 420)" filter="url(#shadow)">
    <rect width="180" height="75" rx="8" fill="#fee2e2" stroke="#dc2626" stroke-width="2"/>
    <text x="90" y="28" text-anchor="middle" font-size="15" font-weight="bold" fill="#7f1d1d">unigraph:Course</text>
    <text x="90" y="48" text-anchor="middle" font-size="11" fill="#991b1b">code : String</text>
    <text x="90" y="64" text-anchor="middle" font-size="11" fill="#991b1b">credits : Integer</text>
  </g>

  <!-- unigraph:CourseSection -->
  <g transform="translate(530, 580)" filter="url(#shadow)">
    <rect width="180" height="75" rx="8" fill="#fee2e2" stroke="#dc2626" stroke-width="2"/>
    <text x="90" y="28" text-anchor="middle" font-size="15" font-weight="bold" fill="#7f1d1d">unigraph:CourseSection</text>
    <text x="90" y="48" text-anchor="middle" font-size="11" fill="#991b1b">sectionNum : Int</text>
    <text x="90" y="64" text-anchor="middle" font-size="11" fill="#991b1b">capacity : Int</text>
  </g>

  <!-- unigraph:Enrollment -->
  <g transform="translate(180, 620)" filter="url(#shadow)">
    <rect width="180" height="75" rx="8" fill="#f1f5f9" stroke="#475569" stroke-width="2"/>
    <text x="90" y="28" text-anchor="middle" font-size="15" font-weight="bold" fill="#0f172a">unigraph:Enrollment</text>
    <text x="90" y="48" text-anchor="middle" font-size="11" fill="#334155">letterGrade : String</text>
    <text x="90" y="64" text-anchor="middle" font-size="11" fill="#334155">gradePoints : Decimal</text>
  </g>

  <!-- unigraph:Semester -->
  <g transform="translate(800, 640)" filter="url(#shadow)">
    <rect width="170" height="70" rx="8" fill="#f8fafc" stroke="#64748b" stroke-width="2"/>
    <text x="85" y="28" text-anchor="middle" font-size="14" font-weight="bold" fill="#0f172a">unigraph:Semester</text>
    <text x="85" y="48" text-anchor="middle" font-size="11" fill="#334155">season : String</text>
    <text x="85" y="64" text-anchor="middle" font-size="11" fill="#334155">year : Integer</text>
  </g>

  <!-- ==================== ARROWS & LABELS ==================== -->
  
  <!-- Subclass arrows (dashed blue) -->
  <!-- Person -> foaf:Person -->
  <line x1="270" y1="260" x2="270" y2="215" stroke="#2563eb" stroke-width="2" stroke-dasharray="5,4" marker-end="url(#arrow-subclass)"/>
  <text x="278" y="240" font-size="10" fill="#2563eb">rdfs:subClassOf</text>

  <!-- Student -> Person -->
  <path d="M 150 370 L 150 330 Q 150 315 220 315 L 220 318" fill="none" stroke="#2563eb" stroke-width="2" stroke-dasharray="5,4" marker-end="url(#arrow-subclass)"/>
  
  <!-- Instructor -> Person -->
  <path d="M 390 370 L 390 330 Q 390 315 320 315 L 320 318" fill="none" stroke="#2563eb" stroke-width="2" stroke-dasharray="5,4" marker-end="url(#arrow-subclass)"/>

  <!-- Professor -> Instructor -->
  <line x1="310" y1="500" x2="350" y2="450" stroke="#2563eb" stroke-width="2" stroke-dasharray="5,4" marker-end="url(#arrow-subclass)"/>

  <!-- Lecturer -> Instructor -->
  <line x1="450" y1="500" x2="420" y2="450" stroke="#2563eb" stroke-width="2" stroke-dasharray="5,4" marker-end="url(#arrow-subclass)"/>

  <!-- Department -> foaf:Organization -->
  <line x1="840" y1="260" x2="840" y2="215" stroke="#2563eb" stroke-width="2" stroke-dasharray="5,4" marker-end="url(#arrow-subclass)"/>
  <text x="848" y="240" font-size="10" fill="#2563eb">rdfs:subClassOf</text>

  <!-- Object Property Arrows -->
  <!-- Instructor advises Student (with subPropertyOf supervises highlight) -->
  <path d="M 300 405 L 246 405" fill="none" stroke="#16a34a" stroke-width="2" marker-end="url(#arrow-green)"/>
  <text x="272" y="398" text-anchor="middle" font-size="10" font-weight="bold" fill="#166534">advises</text>
  <text x="272" y="420" text-anchor="middle" font-size="9" fill="#15803d">(subProp: supervises)</text>

  <!-- Instructor -> Department (belongsToDepartment) -->
  <path d="M 480 395 Q 650 390 750 320" fill="none" stroke="#1e293b" stroke-width="1.5" marker-end="url(#arrow)"/>
  <text x="610" y="375" font-size="10" fill="#1e293b">belongsToDepartment</text>

  <!-- Student -> Program (enrolledInProgram) -->
  <path d="M 170 370 Q 230 280 524 285" fill="none" stroke="#1e293b" stroke-width="1.5" marker-end="url(#arrow)"/>
  <text x="350" y="280" font-size="10" fill="#1e293b">enrolledInProgram</text>

  <!-- Department -> Program (offersProgram) -->
  <line x1="750" y1="290" x2="696" y2="290" stroke="#d97706" stroke-width="1.5" marker-end="url(#arrow)"/>
  <text x="722" y="282" text-anchor="middle" font-size="10" fill="#b45309">offersProg</text>

  <!-- Department -> Course (offersCourse) -->
  <line x1="840" y1="335" x2="840" y2="414" stroke="#d97706" stroke-width="1.5" marker-end="url(#arrow)"/>
  <text x="846" y="380" font-size="10" fill="#b45309">offersCourse</text>

  <!-- CourseSection -> Course (sectionOfCourse) -->
  <path d="M 710 610 Q 770 570 790 500" fill="none" stroke="#dc2626" stroke-width="1.8" marker-end="url(#arrow-red)"/>
  <text x="760" y="565" font-size="10" font-weight="bold" fill="#b91c1c">sectionOfCourse</text>

  <!-- CourseSection -> Instructor (taughtBy) -->
  <path d="M 530 600 Q 420 570 410 450" fill="none" stroke="#dc2626" stroke-width="1.5" marker-end="url(#arrow)"/>
  <text x="440" y="560" font-size="10" fill="#b91c1c">taughtBy</text>

  <!-- CourseSection -> Semester (heldInSemester) -->
  <path d="M 710 640 L 794 665" fill="none" stroke="#1e293b" stroke-width="1.5" marker-end="url(#arrow)"/>
  <text x="740" y="640" font-size="10" fill="#1e293b">heldInSemester</text>

  <!-- Enrollment -> Student & Section -->
  <path d="M 220 620 Q 180 540 160 450" fill="none" stroke="#475569" stroke-width="1.5" marker-end="url(#arrow)"/>
  <text x="140" y="530" font-size="10" fill="#334155">enrollmentStudent</text>

  <line x1="360" y1="640" x2="524" y2="620" stroke="#475569" stroke-width="1.5" marker-end="url(#arrow)"/>
  <text x="430" y="622" font-size="10" fill="#334155">enrollmentSection</text>

  <!-- Course -> Course (hasPrerequisite) -->
  <path d="M 930 440 C 980 430, 980 470, 936 470" fill="none" stroke="#ea580c" stroke-width="1.5" marker-end="url(#arrow)"/>
  <text x="985" y="455" font-size="9" fill="#c2410c">hasPrereq</text>
</svg>
"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)


def generate_png_diagram(output_path: Path) -> None:
    """Generates a raster PNG diagram using Matplotlib."""
    fig, ax = plt.subplots(figsize=(14, 10), dpi=200)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # Background
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#ffffff")

    # Title
    ax.text(50, 97, "UniGraph — University Knowledge Graph Ontology", ha="center", va="top", fontsize=16, fontweight="bold", color="#0f172a")
    ax.text(50, 94, "RDF / RDFS Schema Hierarchy & Vocabulary Integration (FOAF)", ha="center", va="top", fontsize=10, color="#64748b")

    def draw_box(x, y, w, h, label, subtext="", bgcolor="#f8fafc", bordercolor="#64748b", textcolor="#0f172a"):
        rect = patches.FancyBboxPatch(
            (x - w / 2, y - h / 2), w, h,
            boxstyle="round,pad=0.6,rounding_size=1.2",
            facecolor=bgcolor, edgecolor=bordercolor, linewidth=1.5, zorder=3
        )
        ax.add_patch(rect)
        if subtext:
            ax.text(x, y + 1.2, label, ha="center", va="center", fontsize=9.5, fontweight="bold", color=textcolor, zorder=4)
            ax.text(x, y - 1.8, subtext, ha="center", va="center", fontsize=7, color=textcolor, zorder=4)
        else:
            ax.text(x, y, label, ha="center", va="center", fontsize=9.5, fontweight="bold", color=textcolor, zorder=4)

    def draw_arrow(x1, y1, x2, y2, label="", color="#1e293b", style="-", width=1.2, rad=0.0):
        connectionstyle = f"arc3,rad={rad}" if rad != 0 else "arc3,rad=0"
        ax.annotate(
            "", xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(
                arrowstyle="-|>", color=color, lw=width,
                linestyle=style, connectionstyle=connectionstyle,
                mutation_scale=12
            ),
            zorder=2
        )
        if label:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            if rad > 0:
                mx += rad * 10
            elif rad < 0:
                mx -= rad * 10
            ax.text(mx, my + 1, label, ha="center", va="bottom", fontsize=7.5, color=color, fontweight="semibold", zorder=5)

    # Boxes
    # FOAF
    draw_box(25, 84, 20, 7, "foaf:Person", "<<External FOAF>>", "#e0e7ff", "#4338ca", "#312e81")
    draw_box(75, 84, 20, 7, "foaf:Organization", "<<External FOAF>>", "#e0e7ff", "#4338ca", "#312e81")

    # Person hierarchy
    draw_box(25, 70, 20, 7, "unigraph:Person", "subClassOf foaf:Person", "#dcfce7", "#15803d", "#14532d")
    draw_box(13, 54, 18, 9, "unigraph:Student", "status, prog, advisor", "#bbf7d0", "#166534", "#14532d")
    draw_box(37, 54, 18, 9, "unigraph:Instructor", "rank, salary, dept", "#bbf7d0", "#166534", "#14532d")
    draw_box(31, 38, 14, 6, "Professor", "subClassOf Instructor", "#86efac", "#166534", "#14532d")
    draw_box(44, 38, 14, 6, "Lecturer", "subClassOf Instructor", "#86efac", "#166534", "#14532d")

    # Academic Structure
    draw_box(75, 70, 20, 9, "unigraph:Department", "code, budget, name", "#fef3c7", "#d97706", "#78350f")
    draw_box(55, 70, 16, 8, "unigraph:Program", "degreeLevel, credits", "#fef3c7", "#d97706", "#78350f")
    draw_box(75, 48, 20, 9, "unigraph:Course", "code, credits, title", "#fee2e2", "#dc2626", "#7f1d1d")
    draw_box(55, 24, 20, 9, "unigraph:CourseSection", "secNum, cap, semester", "#fee2e2", "#dc2626", "#7f1d1d")

    # Supporting
    draw_box(18, 18, 20, 9, "unigraph:Enrollment", "letterGrade, gradePoints", "#f1f5f9", "#475569", "#0f172a")
    draw_box(82, 24, 18, 8, "unigraph:Semester", "season, year, dates", "#f8fafc", "#64748b", "#0f172a")
    draw_box(82, 10, 16, 6, "unigraph:Room", "capacity, bldg", "#f3e8fd", "#7c3aed", "#581c87")

    # Edges - SubClassOf (Dashed Blue)
    draw_arrow(25, 74, 25, 80, "subClassOf", "#2563eb", "--")
    draw_arrow(13, 59, 23, 66, "subClassOf", "#2563eb", "--")
    draw_arrow(37, 59, 27, 66, "subClassOf", "#2563eb", "--")
    draw_arrow(31, 41, 35, 49, "subClassOf", "#2563eb", "--")
    draw_arrow(44, 41, 39, 49, "subClassOf", "#2563eb", "--")
    draw_arrow(75, 75, 75, 80, "subClassOf", "#2563eb", "--")

    # Object properties
    draw_arrow(28, 54, 22, 54, "advises (subProp supervises)", "#16a34a", "-")
    draw_arrow(46, 56, 65, 68, "belongsToDepartment", "#4b5563", "-")
    draw_arrow(22, 56, 47, 68, "enrolledInProgram", "#4b5563", "-")
    draw_arrow(65, 70, 63, 70, "offersProg", "#d97706", "-")
    draw_arrow(75, 65, 75, 53, "offersCourse", "#dc2626", "-")
    draw_arrow(65, 27, 72, 43, "sectionOfCourse", "#dc2626", "-")
    draw_arrow(47, 27, 39, 49, "taughtBy", "#4b5563", "-")
    draw_arrow(65, 24, 73, 24, "heldInSemester", "#64748b", "-")
    draw_arrow(18, 23, 15, 49, "enrollmentStudent", "#475569", "-")
    draw_arrow(28, 20, 45, 22, "enrollmentSection", "#475569", "-")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def build_all_diagrams():
    """Generates all diagram formats and saves them in ontology/ and docs/."""
    # Mermaid
    mmd_content = generate_mermaid_diagram()
    for d in [ONTOLOGY_DIR, DOCS_DIR]:
        with open(d / "ontology_diagram.mmd", "w", encoding="utf-8") as f:
            f.write(mmd_content)

    # DOT
    dot_content = generate_dot_diagram()
    for d in [ONTOLOGY_DIR, DOCS_DIR]:
        with open(d / "ontology_diagram.dot", "w", encoding="utf-8") as f:
            f.write(dot_content)

    # SVG
    generate_svg_diagram(ONTOLOGY_DIR / "ontology_diagram.svg")
    generate_svg_diagram(DOCS_DIR / "ontology_diagram.svg")

    # PNG
    generate_png_diagram(ONTOLOGY_DIR / "ontology_diagram.png")
    generate_png_diagram(DOCS_DIR / "ontology_diagram.png")


if __name__ == "__main__":
    print("Generating schema visualizations (SVG, PNG, DOT, MMD)...")
    build_all_diagrams()
    print("All ontology diagrams generated successfully in ontology/ and docs/!")
