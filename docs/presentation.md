# Présentation UniGraph — Graphe de Connaissances Universitaire (5 Diapositives)

---

## Diapositive 1 : Problématique et Objectifs

### Contexte & Enjeux
* **Limites des bases de données relationnelles traditionnelles (SGBDR) :**
  * Schémas relationnels rigides, silos d'information et jointures multiples coûteuses.
  * Absence de sémantique formelle compréhensible par des agents automatisés.
  * Impossibilité de déduire de nouvelles connaissances sans coder des règles ad-hoc applicatives.

### Objectifs d'UniGraph
1. **Élever les données universitaires au standard du Web Sémantique (W3C) :**
   * Modélisation ontologique formelle en **RDF / RDFS**.
   * Réutilisation de vocabulaires standards ouverts (**FOAF** pour les personnes et organisations).
2. **Fournir un moteur d'inférence déductif (RDFS Reasoning) :**
   * Exploiter les règles de clôture sémantique (`rdfs7`, `rdfs9`, `rdfs2`, `rdfs3`) pour dériver automatiquement de nouveaux triplets non assertés explicitement.
3. **Interopérabilité & Restitution :**
   * Requêtes expressives via **SPARQL 1.1**.
   * Exposition des données et des déductions via une **API REST Flask** et une interface web interactive.

---

## Diapositive 2 : Jeu de Données & Architecture Globale

### Source des Données Relationnelles
* **Dataset source :** Base de données universitaire échantillon (30 fichiers CSV, 1 000+ enregistrements).
* **Entités clés exploitées :** `departments`, `programs`, `courses`, `instructors`, `students`, `people`, `sections`, `semesters`, `enrollments`, `rooms`, `buildings`.
* **Qualité des données :** 100% d'intégrité référentielle vérifiée ; préservation systématique des identifiants d'origine via `unigraph:sourceId` pour garantir la traçabilité.
* *Note éthique & académique : Données synthétiques à vocation pédagogique sans informations personnelles réelles.*

### Architecture Modulaire du Système
```
[ Données CSV (data/) ] 
         │ (pandas / rdflib)
         ▼
[ Modélisation Ontologique (src/ontology.py) + Conversion RDF (src/converter.py) ]
         │
         ├──► Graphe Brut (data/unigraph.ttl : 15 621 triplets)
         │
         ▼
[ Raisonneur Sémantique RDFS (src/inference.py via owlrl) ]
         │
         ├──► Graphe Inféré (data/unigraph_inferred.ttl : 25 112 triplets, +9 491 déductions)
         │
         ▼
[ Services & Restitution ]
   ├── Moteur SPARQL (src/sparql_service.py) -> 7 requêtes analytiques (.rq)
   ├── API REST Flask (src/api.py) -> 10 endpoints JSON
   └── Tableau de Bord Web (templates/index.html & static/)
```

---

## Diapositive 3 : Ontologie RDF/RDFS et Schéma Graphique

### Conception Ontologique UniGraph (`https://unigraph.org/schema#`)
* **13 Classes RDFS structurées en hiérarchie (`rdfs:subClassOf`) :**
  * `unigraph:Person` $\sqsubseteq$ `foaf:Person` (Spécialisation du standard W3C FOAF).
  * `unigraph:Student` $\sqsubseteq$ `unigraph:Person`.
  * `unigraph:Instructor` $\sqsubseteq$ `unigraph:Person`.
  * `unigraph:Professor` $\sqsubseteq$ `unigraph:Instructor` et `unigraph:Lecturer` $\sqsubseteq$ `unigraph:Instructor`.
  * `unigraph:Department` $\sqsubseteq$ `foaf:Organization`.
  * `Program`, `Course`, `CourseSection`, `Semester`, `Enrollment`, `Room`, `Building`.
* **18 Propriétés avec Domaines et Étendues Stricts (`rdfs:domain` / `rdfs:range`) :**
  * Relations d'héritage de sous-propriétés (`rdfs:subPropertyOf`) :
    * `unigraph:advises` $\sqsubseteq$ `unigraph:supervises` $\sqsubseteq$ `unigraph:associatedWith`.
    * `unigraph:enrolledInSection` $\sqsubseteq$ `unigraph:involvedInCourse`.
* **Schéma Visuel :** Disponible dans `docs/ontology_diagram.svg` et `ontology/ontology_diagram.png`.

---

## Diapositive 4 : Requêtes SPARQL & Démonstration d'Inférence RDFS

### 7 Requêtes Analytiques SPARQL 1.1 Validées
1. **Q1 :** Étudiants et leurs programmes d'études (50 résultats).
2. **Q2 :** Enseignants, rangs académiques et départements (10 résultats).
3. **Q3 :** Catalogue complet des cours par département (600 résultats).
4. **Q4 :** Sections de cours avec enseignants, semestres et salles (40 résultats).
5. **Q5 :** Inscriptions liant étudiants, sections et notes obtenues (1 000 résultats).
6. **Q6 :** Agrégation : Nombre de cours et crédits moyens par département (14 résultats).
7. **Q7 :** Enseignants conseillers et leurs étudiants supervisés (50 résultats).

### Preuves Formelles d'Inférence RDFS (Avant vs Après)

| Démonstration | Axiome Déclaré | Règle W3C | Avant | Après | Nouveaux Triplets Déduits |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Sous-propriété Superviseur** | `advises rdfs:subPropertyOf supervises` | **rdfs7** | 0 | 50 | **+50 triplets** (`supervises`) |
| **Propagation de Sous-classe** | `Student & Instructor rdfs:subClassOf Person rdfs:subClassOf foaf:Person` | **rdfs9** | 0 | 60 | **+60 triplets** (`foaf:Person`) |
| **Implication de Cours** | `enrolledInSection rdfs:subPropertyOf involvedInCourse` | **rdfs7** | 0 | 1 000 | **+1 000 triplets** (`involvedInCourse`) |
| **Rang Enseignant** | `Professor rdfs:subClassOf Instructor` | **rdfs9** | 0 | 10 | **+10 triplets** (`Instructor`) |

*Bilan global : Passage de 15 621 triplets initiaux à 25 112 triplets après clôture déductive (+9 491 déductions vérifiées).*

---

## Diapositive 5 : API REST Flask, Validation par Tests et Conclusion

### Points d'Accès REST JSON
* `GET /api/status` : Métriques globales de santé du graphe et des entités.
* `GET /api/ontology` : Métadonnées du schéma, hiérarchies et domaines/étendues.
* `GET /api/students`, `GET /api/instructors`, `GET /api/courses`, `GET /api/sections`, `GET /api/enrollments`.
* `GET /api/sparql/queries` & `POST /api/sparql/execute` : Exécution dynamique de requêtes SPARQL.
* `GET /api/inference/demo` : Restitution comparative formelle avant/après inférence.

### Validation par Tests Automatisés
* **35 tests unitaires et d'intégration réussis (100% de succès) via `pytest` :**
  * Structure ontologique et axiomes RDFS (5 tests).
  * Génération RDF et traçabilité des identifiants (4 tests).
  * Exécution et conformité des 7 requêtes SPARQL (8 tests).
  * Vérification mathématique des déductions d'inférence (5 tests).
  * Validité HTTP et réponses JSON des endpoints de l'API (13 tests).

### Conclusion & Perspectives
* **Livrable académique complet, modulaire et directement reproductible.**
* **Perspectives :** Extension vers OWL 2 DL (contraintes de cardinalité, classes disjointes) et publication sous forme d'endpoint SPARQL fédéré (Triple Pattern Fragments).
