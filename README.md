# UniGraph — Graphe de Connaissances Universitaire avec Inférence RDFS & API REST

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![RDFLib](https://img.shields.io/badge/RDFLib-7.6.0-red.svg)](https://rdflib.readthedocs.io/)
[![Flask](https://img.shields.io/badge/Flask-3.1.3-black.svg)](https://flask.palletsprojects.com/)
[![Tests](https://img.shields.io/badge/Tests-49%20passed-success.svg)](#tests-et-validation)
[![License](https://img.shields.io/badge/Academic-Project-purple.svg)]()

> **Projet Académique de Web Sémantique :** Modélisation ontologique RDF/RDFS, intégration du standard W3C FOAF, conversion relationnelle vers graphe, clôture déductive RDFS formelle, requêtes SPARQL 1.1, API REST Flask et tableau de bord interactif.

---

## Sommaire

1. [Objectifs du Projet & Architecture Globale](#1-objectifs-du-projet--architecture-globale)
2. [Source du Jeu de Données & Limites](#2-source-du-jeu-de-données--limites)
3. [Ontologie RDF/RDFS & Réutilisation du Vocabulaire FOAF](#3-ontologie-rdfrdfs--réutilisation-du-vocabulaire-foaf)
4. [Transformation des Données CSV en RDF](#4-transformation-des-données-csv-en-rdf)
5. [Requêtes SPARQL & Exemples de Résultats](#5-requêtes-sparql--exemples-de-résultats)
6. [Démonstration de l'Inférence RDFS (Avant vs Après)](#6-démonstration-de-linférence-rdfs-avant-vs-après)
7. [Points d'Accès de l'API REST Flask & Exemples JSON](#7-points-daccès-de-lapi-rest-flask--exemples-json)
8. [Interface Web Interactive](#8-interface-web-interactive)
9. [Instructions d'Installation & Commandes d'Exécution](#9-instructions-dinstallation--commandes-dexécution)
10. [Tests et Validation Automatisée](#10-tests-et-validation-automatisée)
11. [Guide pour la Soutenance Orale](#11-guide-pour-la-soutenance-orale)
12. [Déclaration d'Assistance IA & Règles Éthiques](#12-déclaration-dassistance-ia--règles-éthiques)

---

## 1. Objectifs du Projet & Architecture Globale

### 1.1 Objectifs
Les bases de données relationnelles (SQL) souffrent de schémas rigides en silos, rendant complexe l'intégration de sources hétérogènes et incapables de déduire de nouvelles connaissances par le sens des données.

Le projet **UniGraph** a pour vocation de :
1. **Sémantiser les données relationnelles :** Convertir 30 tables relationnelles en un graphe de triplets RDF respectant les standards du W3C.
2. **Structurer une ontologie RDFS :** Définir des hiérarchies de classes (`rdfs:subClassOf`), de sous-propriétés (`rdfs:subPropertyOf`), ainsi que des domaines (`rdfs:domain`) et étendues (`rdfs:range`).
3. **Réutiliser les standards existants :** Intégrer le vocabulaire W3C **FOAF** (*Friend of a Friend*) pour la modélisation des personnes et des organisations.
4. **Appliquer l'inférence déductive RDFS :** Déduire formellement de nouveaux triplets par clôture déductive (règles `rdfs7`, `rdfs9`, etc.) en fournissant des preuves mathématiques avant/après.
5. **Restituer et interagir :** Mettre à disposition une batterie de requêtes analytiques **SPARQL 1.1**, une **API REST Flask** complète (14 endpoints JSON) et une **interface web** d'exploration.

### 1.2 Architecture du Système

```
                              ┌───────────────────────────────────┐
                              │     Données CSV d'origine         │
                              │ (data/*.csv : 30 tables réelles)  │
                              └─────────────────┬─────────────────┘
                                                │
                                                ▼ [src/converter.py]
┌─────────────────────────────────┐   ┌───────────────────────────────────┐
│     Ontologie RDFS UniGraph     ├──►│        Graphe Brut UniGraph       │
│   (ontology/unigraph_ontology)  │   │   (data/unigraph.ttl : 15 636 T)  │
└─────────────────────────────────┘   └─────────────────┬─────────────────┘
                                                        │
                                                        ▼ [src/inference.py (owlrl CleanRDFS)]
                                      ┌───────────────────────────────────┐
                                      │       Graphe RDFS Étendu          │
                                      │ (data/unigraph_inferred: 23 904 T)│
                                      │   [+8 268 Nouveaux Triplets]      │
                                      └─────────────────┬─────────────────┘
                                                        │
                         ┌──────────────────────────────┴──────────────────────────────┐
                         ▼                                                             ▼
       ┌───────────────────────────────────┐                         ┌───────────────────────────────────┐
       │     Service SPARQL 1.1            │                         │      API REST Flask & Web UI      │
       │   (queries/*.rq : 10 requêtes)    │                         │   (src/api.py : 14 endpoints)     │
       └───────────────────────────────────┘                         └───────────────────────────────────┘
```

### 1.3 Arborescence des Fichiers

```text
UniGraph/
├── data/                                 # Fichiers CSV du dataset et graphes RDF générés
│   ├── departments.csv, courses.csv ...  # 30 fichiers CSV inspectés
│   ├── unigraph.ttl                      # Graphe RDF brut généré (15 636 triplets)
│   ├── unigraph_inferred.ttl             # Graphe après clôture déductive RDFS (23 904 triplets)
│   └── inferred_triples.ttl              # Triplets inférés uniquement (8 268 triplets)
├── ontology/                             # Définition et schémas de l'ontologie
│   ├── unigraph_ontology.ttl             # Spécification formelle RDFS en Turtle
│   ├── ontology_diagram.svg              # Schéma conceptuel vectoriel
│   ├── ontology_diagram.png              # Schéma graphique haute définition
│   ├── ontology_diagram.dot              # Fichier Graphviz DOT
│   └── ontology_diagram.mmd              # Fichier Mermaid
├── queries/                              # Requêtes SPARQL 1.1 sauvegardées (.rq)
│   ├── q1_students_programs.rq           # Étudiants et leurs programmes (50 résultats)
│   ├── q2_instructors_departments.rq     # Enseignants et leurs départements (10 résultats)
│   ├── q3_courses_departments.rq         # Catalogue des cours par département (600 résultats)
│   ├── q4_sections_instructors_semesters.rq # Sections, enseignants et semestres (40 résultats)
│   ├── q5_enrollments_students_sections.rq  # Inscriptions et notes obtenues (1 000 résultats)
│   ├── q6_department_course_counts.rq    # Agrégation : volume de cours par département (14 résultats)
│   ├── q7_advisor_advisees.rq            # Conseillers et étudiants supervisés (50 résultats)
│   ├── q8_programs_departments.rq        # Programmes et leurs départements (40 résultats)
│   ├── q9_student_course_enrollments.rq  # Cursus complet : étudiant → section → cours (1 000 résultats)
│   └── q10_course_prerequisites.rq       # Prérequis de cours (299 résultats)
├── src/                                  # Code source Python modulaire
│   ├── config.py                         # Constantes, chemins et espaces de nommage
│   ├── ontology.py                       # Modélisation programmatique de l'ontologie
│   ├── converter.py                      # Transformateur CSV vers RDF
│   ├── inference.py                      # Moteur d'inférence RDFS et preuves avant/après
│   ├── sparql_service.py                 # Exécuteur de requêtes SPARQL
│   ├── visualizer.py                     # Générateur des diagrammes de l'ontologie
│   └── api.py                            # Serveur d'API REST Flask et contrôleur web
├── templates/                            # Vue HTML
│   └── index.html                        # Interface web interactive moderne
├── static/                               # Fichiers statiques web
│   ├── css/custom.css                    # Feuilles de style
│   └── js/app.js                         # Logique interactive asynchrone (Fetch)
├── tests/                                # Suite de tests automatisés pytest
│   ├── test_ontology.py                  # Tests de l'ontologie et axiomes
│   ├── test_converter.py                 # Tests de la conversion et traçabilité
│   ├── test_sparql.py                    # Tests d'exécution des 10 requêtes SPARQL
│   ├── test_inference.py                 # Tests rigoureux des règles d'inférence et nettoyage sémantique
│   └── test_api.py                       # Tests de conformité des 14 endpoints REST
├── docs/                                 # Documentation & Soutenance
│   ├── presentation.md                   # Présentation synthétique en 5 diapositives
│   ├── presentation.html                 # Diaporama interactif navigable au clavier
│   └── ontology_diagram.svg              # Schéma de l'ontologie
├── requirements.txt                      # Dépendances Python du projet
├── run.py                                # Script CLI unifié d'administration
└── README.md                             # Documentation de référence
```

---

## 2. Source du Jeu de Données & Limites

### 2.1 Inspection du Schéma Réel
Le jeu de données extrait dans `data/` comprend 30 fichiers CSV réels issus d'une base relationnelle universitaire. L'inspection a validé les tables et cardinalités suivantes :
* **`departments.csv` (14 lignes) :** `id`, `code`, `name`, `budget`, `office_room_id`.
* **`programs.csv` (40 lignes) :** `id`, `name`, `degree_level`, `credits_required`, `department_id`.
* **`courses.csv` (600 lignes) :** `id`, `code`, `credits`, `department_id`, `description`, `title`.
* **`instructors.csv` (10 lignes) :** `id`, `department_id`, `person_id`, `rank`, `salary`.
* **`people.csv` (55 lignes) :** `id`, `first_name`, `last_name`, `email`, `phone`, `date_of_birth`, `gender`, `address_id`.
* **`students.csv` (50 lignes) :** `id`, `advisor_instructor_id`, `enrollment_date`, `person_id`, `program_id`, `status`.
* **`sections.csv` (40 lignes) :** `id`, `capacity`, `course_id`, `instructor_id`, `number`, `room_id`, `semester_id`.
* **`semesters.csv` (10 lignes) :** `id`, `end_date`, `season`, `start_date`, `year`.
* **`enrollments.csv` (1 000 lignes) :** `id`, `grade_points`, `letter_grade`, `section_id`, `student_id`.
* **`buildings.csv` (12 lignes)** & **`rooms.csv` (240 lignes)**.

### 2.2 Intégrité Référentielle & Traçabilité
* **Validation des clés étrangères :** 100% des clés (`person_id`, `department_id`, `program_id`, `advisor_instructor_id`, `course_id`, `semester_id`, `student_id`, `section_id`) pointent vers des identifiants valides.
* **Traçabilité totale :** Chaque entité RDF conserve son identifiant relationnel sous le prédicat `unigraph:sourceId` (ex. `unigraph:sourceId "1"^^xsd:string`), permettant une correspondance bijective directe avec le CSV source.

### 2.3 Nature Synthétique & Respect de la Vie Privée
> [!IMPORTANT]
> Les données utilisées sont des **données synthétiques d'entraînement académique** générées pour des bancs d'essai. Elles ne correspondent à aucun étudiant, enseignant ou université réelle. Aucune information privée ou sensible n'est compromise.

---

## 3. Ontologie RDF/RDFS & Réutilisation du Vocabulaire FOAF

L'ontologie est formalisée dans le fichier [`ontology/unigraph_ontology.ttl`](ontology/unigraph_ontology.ttl).

### 3.1 Espaces de Noms (Namespaces)
* `unigraph:` `<https://unigraph.org/schema#>` (Vocabulaire conceptuel)
* `data:` `<https://unigraph.org/data/>` (Instances de données)
* `foaf:` `<http://xmlns.com/foaf/0.1/>` (Vocabulaire externe FOAF W3C)
* `rdf:` `<http://www.w3.org/1999/02/22-rdf-syntax-ns#>`
* `rdfs:` `<http://www.w3.org/2000/01/rdf-schema#>`
* `xsd:` `<http://www.w3.org/2001/XMLSchema#>`

### 3.2 Hiérarchie des Classes (`rdfs:subClassOf`)
UniGraph réutilise le standard international **FOAF** (*Friend of a Friend*) :
* `foaf:Person` (Super-classe externe)
  * `unigraph:Person` (`rdfs:subClassOf foaf:Person`)
    * `unigraph:Student` (`rdfs:subClassOf unigraph:Person`)
    * `unigraph:Instructor` (`rdfs:subClassOf unigraph:Person`)
      * `unigraph:Professor` (`rdfs:subClassOf unigraph:Instructor`)
      * `unigraph:Lecturer` (`rdfs:subClassOf unigraph:Instructor`)
* `foaf:Organization` (Super-classe externe)
  * `unigraph:Department` (`rdfs:subClassOf foaf:Organization`)
* Classes universitaires dédiées : `unigraph:Program`, `unigraph:Course`, `unigraph:CourseSection`, `unigraph:Semester`, `unigraph:Enrollment`, `unigraph:Room`, `unigraph:Building`.

### 3.3 Propriétés, Domaines, Étendues et Sous-propriétés (`rdfs:subPropertyOf`)
L'ontologie définit 19 propriétés formelles dont :
* `unigraph:associatedWith` : domaine `unigraph:Person`, étendue `rdfs:Resource`.
* `unigraph:supervises` : `rdfs:subPropertyOf unigraph:associatedWith` (domaine `Instructor`, étendue `Student`).
* `unigraph:advises` : `rdfs:subPropertyOf unigraph:supervises` (domaine `Instructor`, étendue `Student`).
* `unigraph:belongsToDepartment` : `rdfs:subPropertyOf unigraph:associatedWith` (domaine `Instructor`, étendue `Department`).
* `unigraph:involvedInCourse` : domaine `unigraph:Person`, étendue `rdfs:Resource`.
* `unigraph:enrolledInSection` : `rdfs:subPropertyOf unigraph:involvedInCourse` (domaine `Student`, étendue `CourseSection`).
* `unigraph:enrolledInProgram` : domaine `Student`, étendue `Program`.
* `unigraph:offersCourse` & `unigraph:courseOfDepartment` : liens réciproques Department/Course.
* `unigraph:programOfDepartment` : domaine `Program`, étendue `Department` — lien correct Programme→Département (distinct de `courseOfDepartment`).
* `unigraph:hasOfficeRoom` : domaine `Department`, étendue `Room` — salle administrative du département (distinct de `heldInRoom` réservé aux sections de cours).
* `unigraph:sectionOfCourse`, `unigraph:taughtBy`, `unigraph:heldInSemester`, `unigraph:heldInRoom`.
* Propriétés de typage littéral : `unigraph:code`, `unigraph:credits` (`xsd:integer`), `unigraph:salary` (`xsd:decimal`), `unigraph:letterGrade` (`xsd:string`), `unigraph:gradePoints` (`xsd:decimal`).

### 3.4 Schéma Graphique de l'Ontologie
Le schéma graphique est consultable dans [`ontology/ontology_diagram.svg`](ontology/ontology_diagram.svg) et [`ontology/ontology_diagram.png`](ontology/ontology_diagram.png).

Il peut être régénéré à tout moment via la commande :
```bash
python run.py visualize
```

---

## 4. Transformation des Données CSV en RDF

Le module [`src/converter.py`](src/converter.py) assure la projection sémantique des CSV :
1. **URI Déterministes & Traçables :**
   * Étudiant ID 1 $\rightarrow$ `<https://unigraph.org/data/student/1>`
   * Enseignant ID 2 $\rightarrow$ `<https://unigraph.org/data/instructor/2>`
   * Cours ID 122 $\rightarrow$ `<https://unigraph.org/data/course/122>`
   * Section ID 5 $\rightarrow$ `<https://unigraph.org/data/section/5>`
2. **Jointure Relationnelle en Triplet RDF :**
   * L'entité `people.csv` est jointe avec `students.csv` et `instructors.csv` pour alimenter les propriétés `foaf:name`, `foaf:firstName`, `foaf:lastName`, `foaf:mbox` (`mailto:email`).
3. **Typage Précis (XSD) :**
   * Les crédits sont typés en `xsd:integer`, les dates en `xsd:date`, les budgets et salaires en `xsd:decimal`. Les valeurs manquantes (`NaN`) sont ignorées pour éviter les triplets vides.
4. **Volume généré :**
   * **15 636 triplets** sérialisés dans [`data/unigraph.ttl`](data/unigraph.ttl).

> [!NOTE]
> La propriété `unigraph:programOfDepartment` (Programme→Département) a été ajoutée après l'audit initial pour remplacer l'usage incorrect de `courseOfDepartment` (domaine: Course) sur des nœuds Programme. De même, `unigraph:hasOfficeRoom` remplace `heldInRoom` sur les nœuds Département. Ces corrections évitent une inférence RDFS erronée qui typisait des Programmes en tant que Cours et des Départements en tant que Sections.

---

## 5. Requêtes SPARQL & Exemples de Résultats

Les requêtes sont stockées sous forme de fichiers autonomes dans le dossier [`queries/`](queries/) :

### Requête 1 : Étudiants et leurs programmes (`q1_students_programs.rq`)
```sparql
PREFIX unigraph: <https://unigraph.org/schema#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?student ?studentName ?email ?programName ?degreeLevel ?status
WHERE {
    ?student a unigraph:Student ;
             foaf:name ?studentName ;
             unigraph:enrolledInProgram ?program .
    OPTIONAL { ?student foaf:mbox ?mbox . BIND(STRAFTER(STR(?mbox), "mailto:") AS ?email) }
    OPTIONAL { ?student unigraph:status ?status }
    OPTIONAL { ?program rdfs:label ?programName }
    OPTIONAL { ?program unigraph:degreeLevel ?degreeLevel }
}
ORDER BY ?studentName
```
*Résultat : 50 lignes. Exemple : `Alexandra Hessel`, programme `Research Analytics Design Practice`, diplôme `bachelor`.*

### Requête 2 : Enseignants et leurs départements (`q2_instructors_departments.rq`)
```sparql
PREFIX unigraph: <https://unigraph.org/schema#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT DISTINCT ?instructor ?instructorName ?rank ?salary ?departmentName ?departmentCode
WHERE {
    ?instructor unigraph:belongsToDepartment ?department ;
                foaf:name ?instructorName .
    OPTIONAL { ?instructor unigraph:rank ?rank }
    OPTIONAL { ?instructor unigraph:salary ?salary }
    OPTIONAL { ?department foaf:name ?departmentName }
    OPTIONAL { ?department unigraph:code ?departmentCode }
}
ORDER BY ?departmentName ?instructorName
```
*Résultat : 10 lignes. Exemple : `Dr. Dina Turner`, rang `assistant_professor`, département `Mechanical Engineering`.*

### Requête 3 : Cours et départements (`q3_courses_departments.rq`)
*Résultat : 600 lignes associant chaque cours, son code, ses crédits et son département.*

### Requête 4 : Sections, enseignants et semestres (`q4_sections_instructors_semesters.rq`)
*Résultat : 40 lignes décrivant l'offre de cours par semestre avec salle assignée.*

### Requête 5 : Inscriptions liant étudiants et sections (`q5_enrollments_students_sections.rq`)
*Résultat : 1 000 lignes reliant l'étudiant, la section suivie, la note attribuée (`letterGrade`) et les points (`gradePoints`).*

### Requête 6 : Agrégation du volume de cours par département (`q6_department_course_counts.rq`)
```sparql
PREFIX unigraph: <https://unigraph.org/schema#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?departmentName (COUNT(DISTINCT ?course) AS ?courseCount) (AVG(?credits) AS ?avgCredits)
WHERE {
    ?course a unigraph:Course ;
            unigraph:courseOfDepartment ?department .
    OPTIONAL { ?course unigraph:credits ?credits }
    OPTIONAL { ?department foaf:name ?departmentName }
}
GROUP BY ?departmentName
ORDER BY DESC(?courseCount)
```
*Résultat : 14 départements classés par volume de cours offerts.*

### Requête 7 : Conseillers et étudiants supervisés (`q7_advisor_advisees.rq`)
*Résultat : 50 paires conseiller-étudiant.*

### Requête 8 : Programmes académiques et départements (`q8_programs_departments.rq`)

* **Objectif :** Lister l'ensemble des cursus et programmes académiques dispensés par l'université, leur département responsable, le cycle d'études associé (`degreeLevel`) et le volume total de crédits obligatoires (`creditsRequired`).
* **Variables & relations interrogées :**
  * `?program` : URI de l'entité programme (`a unigraph:Program`).
  * `?programName` : Intitulé officiel du programme d'études (`rdfs:label`).
  * `?degreeLevel` : Niveau de diplôme (ex. `bachelor`, `master`, `doctorate`) via `unigraph:degreeLevel` (*OPTIONAL*).
  * `?creditsRequired` : Total des crédits requis via `unigraph:creditsRequired` (*OPTIONAL*).
  * `?departmentName` : Nom du département académique de rattachement via `foaf:name` (*OPTIONAL*).
  * `?departmentCode` : Code court officiel du département via `unigraph:code` (*OPTIONAL*).
  * **Relation clé :** `?program unigraph:programOfDepartment ?department` (rattachement direct du programme à son département d'enseignement).

```sparql
PREFIX unigraph: <https://unigraph.org/schema#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?program ?programName ?degreeLevel ?creditsRequired ?departmentName ?departmentCode
WHERE {
    ?program a unigraph:Program ;
             rdfs:label ?programName ;
             unigraph:programOfDepartment ?department .
    OPTIONAL { ?program unigraph:degreeLevel ?degreeLevel }
    OPTIONAL { ?program unigraph:creditsRequired ?creditsRequired }
    OPTIONAL { ?department foaf:name ?departmentName }
    OPTIONAL { ?department unigraph:code ?departmentCode }
}
ORDER BY ?departmentName ?programName
```

*Résultat : 40 lignes. Exemple : Programme `<https://unigraph.org/data/program/35>` (`Environmental Computational Health`), niveau `bachelor`, `30` crédits requis, département `Biology` (`CLTK`).*

### Requête 9 : Cursus et inscriptions complètes des étudiants (`q9_student_course_enrollments.rq`)

* **Objectif :** Reconstituer le parcours pédagogique complet des étudiants en liant chaque inscription à sa section, au cours magistral correspondant, au département organisateur et à la note obtenue.
* **Variables & relations interrogées :**
  * `?studentName` : Nom complet de l'étudiant via `?student foaf:name`.
  * `?courseCode` : Code officiel du cours via `?course unigraph:code`.
  * `?courseTitle` : Titre pédagogique du cours via `?course rdfs:label`.
  * `?sectionNumber` : Numéro de section assignée via `?section unigraph:sectionNumber`.
  * `?departmentName` : Département responsable du cours via `?department foaf:name`.
  * `?letterGrade` : Note littérale obtenue à l'évaluation (ex. `A-`, `B+`) via `?enrollment unigraph:letterGrade` (*OPTIONAL*).
  * **Chaîne relationnelle :** `?enrollment a unigraph:Enrollment` $\rightarrow$ `unigraph:enrollmentStudent ?student` $\rightarrow$ `unigraph:enrollmentSection ?section` $\rightarrow$ `unigraph:sectionOfCourse ?course` $\rightarrow$ `unigraph:courseOfDepartment ?department`.

```sparql
PREFIX unigraph: <https://unigraph.org/schema#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?studentName ?courseCode ?courseTitle ?sectionNumber ?departmentName ?letterGrade
WHERE {
    ?enrollment a unigraph:Enrollment ;
                unigraph:enrollmentStudent ?student ;
                unigraph:enrollmentSection ?section .
    ?student foaf:name ?studentName .
    ?section unigraph:sectionOfCourse ?course ;
             unigraph:sectionNumber ?sectionNumber .
    ?course unigraph:code ?courseCode ;
            rdfs:label ?courseTitle ;
            unigraph:courseOfDepartment ?department .
    ?department foaf:name ?departmentName .
    OPTIONAL { ?enrollment unigraph:letterGrade ?letterGrade }
}
ORDER BY ?studentName ?courseCode
```

*Résultat : 1 000 lignes. Exemple : `Alexandra Hessel`, cours `BJKN-995` (*Principles To Algorithms Calculus*), section `1`, département `Mechanical Engineering`, note `B+`.*

### Requête 10 : Arborescence des prérequis de cours (`q10_course_prerequisites.rq`)

* **Objectif :** Modéliser et explorer les dépendances pédagogiques du catalogue universitaire en reliant chaque cours cible à son cours obligatoire prérequis.
* **Variables & relations interrogées :**
  * `?courseCode` : Code officiel du cours cible via `?course unigraph:code`.
  * `?courseTitle` : Titre du cours cible via `?course rdfs:label`.
  * `?prerequisiteCode` : Code du cours prérequis via `?prereq unigraph:code`.
  * `?prerequisiteTitle` : Titre du cours prérequis via `?prereq rdfs:label`.
  * **Relation clé :** `?course unigraph:hasPrerequisite ?prereq` reliant deux cours distincts (`unigraph:Course`).

```sparql
PREFIX unigraph: <https://unigraph.org/schema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?courseCode ?courseTitle ?prerequisiteCode ?prerequisiteTitle
WHERE {
    ?course a unigraph:Course ;
            unigraph:code ?courseCode ;
            rdfs:label ?courseTitle ;
            unigraph:hasPrerequisite ?prereq .
    ?prereq unigraph:code ?prerequisiteCode ;
            rdfs:label ?prerequisiteTitle .
}
ORDER BY ?courseCode ?prerequisiteCode
```

*Résultat : 299 lignes (sur 300 dépendances CSV sources, 1 auto-dépendance invalide ayant été assainie à la conversion). Exemple : Le cours `ABLO-358` (*To Of Foundations*) requiert le cours préalable `MZXR-857` (*Statistics Design Algorithms Analysis*).*

---

## 6. Démonstration de l'Inférence RDFS (Avant vs Après)

L'inférence sémantique est calculée par le module [`src/inference.py`](src/inference.py) via `owlrl.DeductiveClosure(CleanRDFS_Semantics)`.

> [!IMPORTANT]
> **Correction d'un bug d'inférence critique :** La classe `owlrl.RDFS_Semantics` contient une règle cachée `one_time_rules()` qui duplique les littéraux `xsd:integer` en `xsd:decimal` (ex: crédits `1` → `1.0`). Cette duplication déclenchait à tort la propagation de `rdfs:domain` et typait des nœuds **Programme** comme `unigraph:Course` et des nœuds **Département** comme `unigraph:CourseSection`. La sous-classe `CleanRDFS_Semantics` remplace `one_time_rules()` par une méthode vide pour éliminer ce comportement.

### 6.1 Bilan Quantitatif Global
* **Triplets initiaux (bruts) :** `15 636`
* **Triplets après clôture RDFS (propre) :** `23 904`
* **Nouveaux triplets déduits :** **`+8 268`**
* Fichiers générés : `data/unigraph_inferred.ttl` (graphe complet) et `data/inferred_triples.ttl` (triplets déduits isolés).

### 6.2 Preuves Expérimentales Détaillées

```
+-------------------------------------------------------------------------------------------------------+
| Démonstration 1 : Héritage de sous-propriété (Règle W3C rdfs7)                                         |
+-------------------------------------------------------------------------------------------------------+
| Axiome formel    : unigraph:advises rdfs:subPropertyOf unigraph:supervises                             |
| Règle W3C rdfs7  : (?p rdfs:subPropertyOf ?q) ∧ (?s ?p ?o) ⟹ (?s ?q ?o)                                |
| Donnée brute     : <data:instructor/3> unigraph:advises <data:student/1>                               |
|                                                                                                       |
| Triplets (?i unigraph:supervises ?s) AVANT inférence : 0                                              |
| Triplets (?i unigraph:supervises ?s) APRÈS inférence : 50 (+50 triplets déduits formellement)         |
+-------------------------------------------------------------------------------------------------------+

+-------------------------------------------------------------------------------------------------------+
| Démonstration 2 : Propagation de classe dans la hiérarchie FOAF (Règle W3C rdfs9)                     |
+-------------------------------------------------------------------------------------------------------+
| Axiome formel    : unigraph:Student rdfs:subClassOf unigraph:Person ∧                                  |
|                    unigraph:Person rdfs:subClassOf foaf:Person                                        |
| Règle W3C rdfs9  : (?c rdfs:subClassOf ?d) ∧ (?x rdf:type ?c) ⟹ (?x rdf:type ?d)                        |
| Donnée brute     : Seul le type unigraph:Student ou unigraph:Instructor est asserté dans les données.  |
|                    Aucun individu n'est typé explicitement en foaf:Person.                            |
|                                                                                                       |
| Instances de (?x rdf:type foaf:Person) AVANT inférence : 0                                            |
| Instances de (?x rdf:type foaf:Person) APRÈS inférence : 60 (50 étudiants + 10 enseignants déduits !)   |
+-------------------------------------------------------------------------------------------------------+

+-------------------------------------------------------------------------------------------------------+
| Démonstration 3 : Raccourci d'inscription vers implication de cours (Règle W3C rdfs7)                 |
+-------------------------------------------------------------------------------------------------------+
| Axiome formel    : unigraph:enrolledInSection rdfs:subPropertyOf unigraph:involvedInCourse             |
| Donnée brute     : Assertions d'inscriptions directes dans les sections.                              |
|                                                                                                       |
| Triplets (?s unigraph:involvedInCourse ?sec) AVANT inférence : 0                                      |
| Triplets (?s unigraph:involvedInCourse ?sec) APRÈS inférence : 1 000 (+1 000 triplets déduits)        |
+-------------------------------------------------------------------------------------------------------+

+-------------------------------------------------------------------------------------------------------+
| Démonstration 4 : Rangs académiques vers Instructeur général (Règle W3C rdfs9)                        |
+-------------------------------------------------------------------------------------------------------+
| Axiome formel    : unigraph:Professor rdfs:subClassOf unigraph:Instructor                              |
| Triplets (?i rdf:type unigraph:Instructor) AVANT inférence : 0 (seul Professor ou Lecturer asserté)   |
| Triplets (?i rdf:type unigraph:Instructor) APRÈS inférence : 10 (+10 enseignants déduits)            |
+-------------------------------------------------------------------------------------------------------+
```

---

## 7. Points d'Accès de l'API REST Flask & Exemples JSON

L'API REST est implémentée dans [`src/api.py`](src/api.py). Elle retourne des réponses JSON conformes avec gestion systématique des codes de statut HTTP (`200`, `400`, `404`, `500`) et support CORS.

### Résumé des 14 Endpoints

| Méthode | Route | Description | Exemple de Paramètre |
| :---: | :--- | :--- | :--- |
| `GET` | `/api/status` | Métriques globales et état de santé du graphe | Aucun |
| `GET` | `/api/ontology` | Structure des classes, propriétés et axiomes | Aucun |
| `GET` | `/api/students` | Liste des étudiants, programmes et conseillers | `?limit=10&status=enrolled` |
| `GET` | `/api/instructors` | Liste des enseignants et départements | `?department=Engineering&rank=professor` |
| `GET` | `/api/departments` | Liste des 14 départements avec budgets | Aucun |
| `GET` | `/api/programs` | Liste des 40 programmes par département | `?limit=20&department=Computer` |
| `GET` | `/api/courses` | Catalogue des cours et crédits | `?limit=5&department=Physics` |
| `GET` | `/api/sections` | Sections de cours, horaires et semestres | Aucun |
| `GET` | `/api/enrollments` | Inscriptions des étudiants et notes obtenues | `?limit=10` |
| `GET` | `/api/sparql/queries` | Liste des 10 requêtes SPARQL pré-configurées | Aucun |
| `POST` | `/api/sparql/execute` | Exécuteur dynamique SPARQL (brut ou inféré) | Body JSON |
| `GET` | `/api/inference/demo` | Rapport complet des démonstrations avant/après | Aucun |
| `GET` | `/api/export/<target>` | Téléchargement des graphes Turtle ou du diagramme | `raw`, `inferred`, `inferred_only`, `ontology`, `diagram` |
| `GET` | `/` | Interface web interactive | Aucun |

### Exemples de Réponses JSON

#### 1. `GET /api/status`
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "service": "UniGraph REST API",
    "version": "1.0.0",
    "graph_statistics": {
      "raw_triples": 15636,
      "inferred_triples_total": 23904,
      "newly_inferred_triples": 8268
    },
    "entity_counts": {
      "students": 50,
      "instructors": 10,
      "departments": 14,
      "programs": 40,
      "courses": 600,
      "sections": 40,
      "enrollments": 1000
    }
  }
}
```

#### 2. `GET /api/students?limit=1`
```json
{
  "success": true,
  "count": 1,
  "data": [
    {
      "student": "https://unigraph.org/data/student/27",
      "studentName": "Alexandra Hessel",
      "email": "alexandra_hessel@hotmail.com",
      "programName": "Research Analytics Design Practice",
      "degreeLevel": "bachelor",
      "status": "graduated",
      "advisorName": "Dina Turner"
    }
  ]
}
```

#### 3. `POST /api/sparql/execute`
*Requête (Body) :*
```json
{
  "query_id": "q2_instructors_departments",
  "use_inferred": false
}
```
*Réponse :*
```json
{
  "success": true,
  "count": 10,
  "execution_time_seconds": 0.0249,
  "variables": ["instructor", "instructorName", "rank", "salary", "departmentName", "departmentCode"],
  "results": [
    {
      "instructor": "https://unigraph.org/data/instructor/1",
      "instructorName": "Dina Turner",
      "rank": "assistant_professor",
      "salary": "96928.75",
      "departmentName": "Mechanical Engineering",
      "departmentCode": "SNNA"
    }
  ],
  "error": null
}
```

---

## 8. Interface Web Interactive

Le serveur intègre une interface web accessible à la racine (`http://127.0.0.1:5000/`) :
* **Tableau de Bord :** Statistiques en direct, métriques de clôture sémantique et aperçu du schéma.
* **Explorateur d'Ontologie :** Visualisation graphique vectorielle SVG et tables des axiomes RDFS.
* **Explorateur d'Entités :** Navigation paginée et filtrée dans les étudiants, enseignants, cours, sections et inscriptions.
* **Console SPARQL :** Éditeur de requête avec chargement en 1 clic des requêtes types, bascule d'exécution (graphe brut vs inféré) et tableau de résultats paginé.
* **Laboratoire d'Inférence RDFS :** Panneaux interactifs présentant les règles formelles (`rdfs7`, `rdfs9`), les métriques comparatives et les triplets déduits.
* **Testeur d'API REST :** Modal de test en direct pour exécuter et prévisualiser les réponses JSON de chaque endpoint.

---

## 9. Instructions d'Installation & Commandes d'Exécution

### 9.1 Prérequis
* Python **3.10+** (testé sous Python 3.12).
* Gestionnaire de paquets `pip`.

### 9.2 Installation des Dépendances
Dans le répertoire racine du projet :
```bash
pip install -r requirements.txt
```

### 9.3 Commandes Unifiées du Projet (`run.py`)

Le script `run.py` fournit une interface CLI complète :

```bash
# 1. Construire l'ontologie et convertir les fichiers CSV en RDF Turtle (data/unigraph.ttl)
python run.py build

# 2. Exécuter le raisonneur RDFS et générer le graphe inféré (data/unigraph_inferred.ttl)
python run.py infer

# 3. Générer les visualisations de l'ontologie (SVG, PNG, DOT, Mermaid)
python run.py visualize

# 4. Lancer la suite de tests automatisés pytest
python run.py test

# 5. Exécuter une requête SPARQL spécifique depuis le terminal
python run.py query q1_students_programs
python run.py query q7_advisor_advisees --inferred

# 6. Démarrer l'API REST Flask et l'interface Web interactive (Port 5000)
python run.py serve

# 7. Pipeline complet en une seule commande (build + infer + visualize + test)
python run.py all
```

Une fois le serveur lancé (`python run.py serve`), ouvrez votre navigateur à l'adresse :
👉 **http://127.0.0.1:5000**

---

## 10. Tests et Validation Automatisée

Le projet intègre **49 tests automatisés** sous `pytest` couvrant l'intégralité du cycle de vie des données sémantiques :

```bash
pytest -v
```

### Détail des 49 Tests Réussis

* **Ontologie & Axiomes (`test_ontology.py` - 5 tests) :**
  * `test_ontology_classes_count` : Présence de $\ge 5$ classes RDFS (13 définies).
  * `test_ontology_properties_count` : Présence de $\ge 8$ propriétés (19 définies).
  * `test_subclass_hierarchy` : Vérification des hiérarchies `rdfs:subClassOf` et intégration de `foaf:Person`.
  * `test_subproperty_relationship` : Vérification de `unigraph:advises rdfs:subPropertyOf unigraph:supervises`.
  * `test_property_domains_and_ranges` : Contrôle des domaines et étendues (`rdfs:domain` et `rdfs:range`) dont `programOfDepartment` et `hasOfficeRoom`.
* **Génération RDF & Traçabilité (`test_converter.py` - 5 tests) :**
  * `test_triple_count` : Volume supérieur à 10 000 triplets (15 636 validés).
  * `test_entity_types_present` : Comptage strict de toutes les entités relationnelles converties (50 étudiants, 600 cours, 14 départements...).
  * `test_source_id_traceability` : Présence des identifiants `unigraph:sourceId` et `unigraph:sourcePersonId`.
  * `test_clean_property_usage` : Vérification sémantique qu'aucun Programme n'utilise `courseOfDepartment` et qu'aucun Département n'utilise `heldInRoom`.
  * `test_foaf_integration` : Rattachement systématique des propriétés `foaf:name` et `foaf:mbox`.
* **Moteur SPARQL (`test_sparql.py` - 13 tests) :**
  * `test_list_queries` : Disponibilité de l'ensemble des requêtes pré-définies.
  * Validation syntaxique et exécution des requêtes `q1` à `q10` avec vérification stricte des résultats attendus.
  * `test_query_empty_results` & `test_query_invalid_syntax` : Gestion des requêtes sans correspondance et erreurs de syntaxe.
* **Raisonnement Sémantique (`test_inference.py` - 6 tests) :**
  * `test_inferred_triples_exist` : Preuve de la déduction de nouveaux triplets par clôture déductive.
  * `test_demo1_subproperty_supervises` : Règle `rdfs7` sur `supervises` (0 avant $\rightarrow$ 50 après).
  * `test_demo2_subclass_foaf_person` : Règle `rdfs9` sur `foaf:Person` (0 avant $\rightarrow$ 60 après).
  * `test_demo3_subproperty_involved` : Règle `rdfs7` sur `involvedInCourse` (0 avant $\rightarrow$ 1 000 après).
  * `test_demo4_subclass_instructor` : Règle `rdfs9` sur `Instructor` (0 avant $\rightarrow$ 10 après).
  * `test_semantic_cleanliness` : Garantie d'absence de typages parasites (0 Programme typé en Course, 0 Département typé en Section).
* **API REST Flask (`test_api.py` - 20 tests) :**
  * Validation des statuts HTTP `200` et formats JSON de tous les endpoints (`/api/status`, `/api/ontology`, `/api/students`, `/api/instructors`, `/api/departments`, `/api/programs`, `/api/courses`, `/api/sections`, `/api/enrollments`, `/api/sparql/queries`, `/api/sparql/execute`, `/api/inference/demo`).
  * Tests d'exécution SPARQL par identifiant prédéfini et par chaîne personnalisée.
  * Validation des statuts `400 Bad Request` sur syntaxe invalide, limite négative ou non-entière, corps vide, corps non-dict.
  * Validation des statuts `404 Not Found` sur routes inexistantes et query_id inconnu.
  * Téléchargement des exports Turtle (`inferred_only`).

---

## 11. Guide pour la Soutenance Orale

Voici les points clés à mettre en avant lors de la soutenance :

### 1. Introduction & Problématique (1 min)
* Expliquez pourquoi le relationnel classique ne suffit pas pour représenter le sens d'un campus universitaire : absence d'inférence, vocabulaires propriétaires non réutilisables.
* Présentez l'objectif d'UniGraph : passer d'un schéma tabulaire à un graphe interconnecté au standard W3C.

### 2. Ontologie et Choix de Modélisation (2 min)
* **Réutilisation de FOAF :** Montrez que `unigraph:Person` hérite de `foaf:Person` et que `unigraph:Department` hérite de `foaf:Organization`. Cela permet à tout agent sémantique externe de comprendre immédiatement qui sont les personnes de notre université.
* **Hiérarchie de Propriétés :** Expliquez la distinction sémantique entre `advises` (relation étroite de mentorat) et `supervises` (supervision académique plus large).

### 3. Le Pouvoir de l'Inférence RDFS (3 min)
* C'est le cœur théorique du projet : ouvrez l'onglet **Inférence** de l'interface web ou montrez les résultats de `python run.py infer`.
* Montrez l'exemple concret : **Dans le fichier CSV, aucun enseignant n'est typé en `foaf:Person`. Pourtant, après application de la règle `rdfs9`, 60 personnes sont formellement reconnues comme des personnes FOAF !**
* De même pour `unigraph:advises` $\rightarrow$ `unigraph:supervises` via la règle `rdfs7`.

### 4. Démonstration Technique & API (3 min)
* Ouvrez l'interface web locale (`http://127.0.0.1:5000`).
* Lancez une requête SPARQL (par exemple `q6_department_course_counts`).
* Montrez la console API REST en direct ou le terminal avec les 49 tests réussis (`pytest`).

### 5. Questions Fréquentes du Jury

* **Q : Pourquoi avoir séparé le graphe brut du graphe inféré ?**  
  *R :* Pour pouvoir quantifier et prouver rigoureusement ce que le raisonneur a apporté (+8 268 triplets), sans jamais confondre ce qui relève de l'assertion explicite et de la déduction logique.
* **Q : Comment garantissez-vous qu'aucune donnée n'a été inventée ?**  
  *R :* Chaque entité conserve sa clé d'origine via `unigraph:sourceId` et le script `inspect_dataset.py` a validé au préalable les 30 tables CSV sources.
* **Q : Quelle est la différence entre RDFS et OWL ?**  
  *R :* RDFS permet de déduire des sous-classes (`rdfs:subClassOf`), sous-propriétés (`rdfs:subPropertyOf`), domaines et étendues. OWL apporterait des contraintes supplémentaires comme les classes disjointes (`owl:disjointWith`) ou les propriétés inverses (`owl:inverseOf`).

---

## 12. Déclaration d'Assistance IA & Règles Éthiques

Conformément aux directives de transparence académique :
* **Assistance IA :** Ce projet a été développé en binôme d'ingénierie assistée par modèle de raisonnement IA pour la formalisation du code modulaire, la rédaction des tests unitaires et la documentation francophone.
* **Vérification humaine et reproductibilité :** Tous les scripts, ontologies, requêtes SPARQL et tests ont été exécutés, validés et testés avec succès dans l'environnement Python de l'hôte.
* **Sécurité & Confidentialité :** Aucun secret, mot de passe ou clé API n'est présent dans le projet. Les chemins sont relatifs et portables.
