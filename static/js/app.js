// UniGraph Web Dashboard Frontend Application

let currentSavedQueries = [];

document.addEventListener("DOMContentLoaded", () => {
    initNavigation();
    loadStatus();
    loadOntologyInfo();
    loadSavedQueries();
    loadInferenceDemos();
    loadStudents();
});

// Navigation Handling
function initNavigation() {
    const navButtons = document.querySelectorAll(".navbar-nav button[data-section]");
    navButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetSection = btn.getAttribute("data-section");
            switchSection(targetSection);
        });
    });
}

function switchSection(sectionId) {
    document.querySelectorAll(".navbar-nav button[data-section]").forEach(b => {
        if (b.getAttribute("data-section") === sectionId) {
            b.classList.add("active");
            b.classList.remove("text-white-50");
        } else {
            b.classList.remove("active");
            b.classList.add("text-white-50");
        }
    });

    document.querySelectorAll(".content-section").forEach(sec => {
        sec.classList.add("d-none");
    });

    const activeSec = document.getElementById(`section-${sectionId}`);
    if (activeSec) {
        activeSec.classList.remove("d-none");
    }
}

// 1. Status & Stats Loading
async function loadStatus() {
    try {
        const resp = await fetch("/api/status");
        const json = await resp.json();
        if (json.success) {
            const data = json.data;
            document.getElementById("stat-raw-triples").textContent = data.graph_statistics.raw_triples.toLocaleString();
            document.getElementById("stat-inf-triples").textContent = data.graph_statistics.inferred_triples_total.toLocaleString();
            document.getElementById("stat-inf-delta").textContent = `+${data.graph_statistics.newly_inferred_triples.toLocaleString()} déduits par RDFS`;
            document.getElementById("stat-people").textContent = `${data.entity_counts.students} étud. / ${data.entity_counts.instructors} ens.`;
            document.getElementById("stat-courses").textContent = `${data.entity_counts.courses} cours`;
            document.getElementById("stat-enrollments").textContent = `${data.entity_counts.enrollments} inscriptions`;
        }
    } catch (err) {
        console.error("Error loading status:", err);
    }
}

// 2. Ontology Loading
async function loadOntologyInfo() {
    try {
        const resp = await fetch("/api/ontology");
        const json = await resp.json();
        if (json.success) {
            const data = json.data;
            
            // Populate classes table
            const cTbody = document.getElementById("ontology-classes-tbody");
            cTbody.innerHTML = data.classes.map(c => `
                <tr>
                    <td class="fw-semibold text-primary font-monospace">${c.label}</td>
                    <td>${c.subClassOf ? `<span class="badge bg-primary-subtle text-primary border">${c.subClassOf}</span>` : '<span class="text-muted">rdfs:Class</span>'}</td>
                </tr>
            `).join("");

            // Populate properties table
            const pTbody = document.getElementById("ontology-properties-tbody");
            pTbody.innerHTML = data.properties.map(p => `
                <tr>
                    <td class="fw-semibold font-monospace">${p.label}</td>
                    <td><span class="badge bg-secondary-subtle text-secondary">${p.domain || 'Resource'}</span></td>
                    <td><span class="badge bg-info-subtle text-info">${p.range || 'Resource'}</span></td>
                    <td>${p.subPropertyOf ? `<span class="badge bg-warning-subtle text-dark border">${p.subPropertyOf}</span>` : '<span class="text-muted">-</span>'}</td>
                </tr>
            `).join("");
        }
    } catch (err) {
        console.error("Error loading ontology:", err);
    }
}

// 3. Entity Data Tables Loading
async function loadStudents() {
    const tbody = document.querySelector("#students-table tbody");
    tbody.innerHTML = '<tr><td colspan="6" class="text-center py-4 text-muted">Chargement...</td></tr>';
    try {
        const resp = await fetch("/api/students?limit=50");
        const json = await resp.json();
        if (json.success) {
            tbody.innerHTML = json.data.map(s => `
                <tr>
                    <td class="fw-semibold">${s.studentName || '-'}</td>
                    <td>${s.email ? `<a href="mailto:${s.email}">${s.email}</a>` : '-'}</td>
                    <td>${s.programName || '-'}</td>
                    <td><span class="badge bg-light text-dark border">${s.degreeLevel || '-'}</span></td>
                    <td>${s.advisorName || '<span class="text-muted">Aucun</span>'}</td>
                    <td><span class="badge bg-${s.status === 'graduated' ? 'success' : 'primary'}-subtle text-${s.status === 'graduated' ? 'success' : 'primary'}">${s.status || '-'}</span></td>
                </tr>
            `).join("");
        }
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-danger py-3 text-center">Erreur : ${err.message}</td></tr>`;
    }
}

async function loadInstructors() {
    const tbody = document.querySelector("#instructors-table tbody");
    tbody.innerHTML = '<tr><td colspan="5" class="text-center py-4 text-muted">Chargement...</td></tr>';
    try {
        const resp = await fetch("/api/instructors");
        const json = await resp.json();
        if (json.success) {
            tbody.innerHTML = json.data.map(i => `
                <tr>
                    <td class="fw-semibold">${i.instructorName || '-'}</td>
                    <td>${i.email ? `<a href="mailto:${i.email}">${i.email}</a>` : '-'}</td>
                    <td><span class="badge bg-primary-subtle text-primary">${i.rank || '-'}</span></td>
                    <td>${i.departmentName || '-'} (${i.departmentCode || '-'})</td>
                    <td>${i.salary ? Number(i.salary).toLocaleString('fr-FR', {style: 'currency', currency: 'EUR'}) : '-'}</td>
                </tr>
            `).join("");
        }
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-danger py-3 text-center">Erreur : ${err.message}</td></tr>`;
    }
}

async function loadCourses() {
    const tbody = document.querySelector("#courses-table tbody");
    tbody.innerHTML = '<tr><td colspan="4" class="text-center py-4 text-muted">Chargement...</td></tr>';
    try {
        const resp = await fetch("/api/courses?limit=100");
        const json = await resp.json();
        if (json.success) {
            tbody.innerHTML = json.data.map(c => `
                <tr>
                    <td class="font-monospace fw-semibold text-primary">${c.courseCode || '-'}</td>
                    <td>${c.title || '-'}</td>
                    <td><span class="badge bg-light text-dark border">${c.credits || '-'} crédits</span></td>
                    <td>${c.departmentName || '-'}</td>
                </tr>
            `).join("");
        }
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="4" class="text-danger py-3 text-center">Erreur : ${err.message}</td></tr>`;
    }
}

async function loadSections() {
    const tbody = document.querySelector("#sections-table tbody");
    tbody.innerHTML = '<tr><td colspan="7" class="text-center py-4 text-muted">Chargement...</td></tr>';
    try {
        const resp = await fetch("/api/sections");
        const json = await resp.json();
        if (json.success) {
            tbody.innerHTML = json.data.map(sec => `
                <tr>
                    <td class="font-monospace fw-semibold">${sec.courseCode || '-'}</td>
                    <td>${sec.courseTitle || '-'}</td>
                    <td>Section ${sec.sectionNumber || '-'}</td>
                    <td>${sec.instructorName || '-'}</td>
                    <td><span class="badge bg-secondary-subtle text-secondary">${sec.semesterLabel || '-'}</span></td>
                    <td>${sec.roomLabel || '-'}</td>
                    <td>${sec.capacity || '-'} places</td>
                </tr>
            `).join("");
        }
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-danger py-3 text-center">Erreur : ${err.message}</td></tr>`;
    }
}

async function loadEnrollments() {
    const tbody = document.querySelector("#enrollments-table tbody");
    tbody.innerHTML = '<tr><td colspan="6" class="text-center py-4 text-muted">Chargement...</td></tr>';
    try {
        const resp = await fetch("/api/enrollments?limit=100");
        const json = await resp.json();
        if (json.success) {
            tbody.innerHTML = json.data.map(e => `
                <tr>
                    <td class="fw-semibold">${e.studentName || '-'}</td>
                    <td class="font-monospace text-primary">${e.courseCode || '-'}</td>
                    <td>${e.courseTitle || '-'}</td>
                    <td>Section ${e.sectionNumber || '-'}</td>
                    <td><span class="badge bg-success-subtle text-success">${e.letterGrade || '-'}</span></td>
                    <td>${e.gradePoints || '-'}</td>
                </tr>
            `).join("");
        }
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-danger py-3 text-center">Erreur : ${err.message}</td></tr>`;
    }
}

// 4. SPARQL Console
async function loadSavedQueries() {
    try {
        const resp = await fetch("/api/sparql/queries");
        const json = await resp.json();
        if (json.success) {
            currentSavedQueries = json.data;
            const select = document.getElementById("saved-queries-select");
            select.innerHTML = '<option value="">-- Choisir une requête pré-définie --</option>' +
                currentSavedQueries.map(q => `<option value="${q.id}">${q.title}</option>`).join("");
            
            // Default load query 1
            if (currentSavedQueries.length > 0) {
                select.value = currentSavedQueries[0].id;
                onSelectSavedQuery();
            }
        }
    } catch (err) {
        console.error("Error loading queries:", err);
    }
}

function onSelectSavedQuery() {
    const select = document.getElementById("saved-queries-select");
    const queryId = select.value;
    const selected = currentSavedQueries.find(q => q.id === queryId);
    if (selected) {
        document.getElementById("sparql-editor").value = selected.query;
        document.getElementById("selected-query-description").textContent = selected.description;
    }
}

async function executeSparql() {
    const query = document.getElementById("sparql-editor").value;
    const useInferred = document.getElementById("sparql-use-inferred").checked;
    const countBadge = document.getElementById("badge-query-count");
    const timeBadge = document.getElementById("badge-query-time");
    const table = document.getElementById("sparql-results-table");

    countBadge.textContent = "Exécution...";
    table.querySelector("thead").innerHTML = '<tr><th class="text-center py-3">Chargement des résultats...</th></tr>';
    table.querySelector("tbody").innerHTML = "";

    try {
        const resp = await fetch("/api/sparql/execute", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: query, use_inferred: useInferred })
        });
        const res = await resp.json();

        if (res.success) {
            countBadge.textContent = `${res.count} résultat(s)`;
            timeBadge.textContent = `${res.execution_time_seconds}s`;

            if (res.variables.length === 0 || res.results.length === 0) {
                table.querySelector("thead").innerHTML = '<tr><th class="text-center text-muted py-4">Aucun résultat trouvé pour cette requête.</th></tr>';
                return;
            }

            // Headers
            table.querySelector("thead").innerHTML = `<tr>${res.variables.map(v => `<th class="bg-light">${v}</th>`).join("")}</tr>`;

            // Rows
            table.querySelector("tbody").innerHTML = res.results.map(row => `
                <tr>
                    ${res.variables.map(v => {
                        const val = row[v] || "";
                        const isUri = val.startsWith("http://") || val.startsWith("https://");
                        return `<td class="${isUri ? 'font-monospace text-truncate' : ''}" style="max-width: 260px;" title="${val}">${isUri ? `<span class="text-primary">${val.split(/[\/#]/).pop()}</span>` : val}</td>`;
                    }).join("")}
                </tr>
            `).join("");
        } else {
            countBadge.textContent = "Erreur";
            timeBadge.textContent = `${res.execution_time_seconds || 0}s`;
            table.querySelector("thead").innerHTML = `<tr><th class="text-danger py-4 text-center">Erreur SPARQL : ${res.error}</th></tr>`;
        }
    } catch (err) {
        countBadge.textContent = "Erreur réseau";
        table.querySelector("thead").innerHTML = `<tr><th class="text-danger py-4 text-center">${err.message}</th></tr>`;
    }
}

// 5. RDFS Inference Laboratory
async function loadInferenceDemos() {
    const container = document.getElementById("inference-cards-container");
    container.innerHTML = '<div class="col-12 text-center py-4 text-muted">Chargement des preuves d\'inférence...</div>';
    try {
        const resp = await fetch("/api/inference/demo");
        const json = await resp.json();
        if (json.success) {
            const data = json.data;
            const demos = data.demonstrations;

            container.innerHTML = Object.entries(demos).map(([key, d]) => `
                <div class="col-lg-6">
                    <div class="card demo-card shadow-sm border-0 h-100">
                        <div class="card-header bg-white py-3 border-bottom d-flex justify-content-between align-items-center">
                            <div>
                                <span class="badge bg-primary text-white me-2">Règle ${d.rule.toUpperCase()}</span>
                                <span class="fw-bold text-navy">${d.rule_name}</span>
                            </div>
                            <span class="badge bg-success-subtle text-success border border-success">+${d.inferred_count} déduits</span>
                        </div>
                        <div class="card-body">
                            <h6 class="fw-bold text-navy mb-2">${d.title}</h6>
                            <div class="p-2 mb-3 bg-light rounded font-monospace fs-8 border text-secondary">
                                <strong>Axiome :</strong> ${d.axiom}<br>
                                <strong>Définition :</strong> ${d.formal_definition}
                            </div>
                            <p class="text-muted fs-8 mb-3">${d.description}</p>
                            
                            <div class="row g-2 mb-3">
                                <div class="col-6">
                                    <div class="demo-metric-box bg-light border text-center">
                                        <div class="text-muted fs-8 text-uppercase">Avant Inférence</div>
                                        <div class="fs-4 fw-bold text-dark">${d.before_count}</div>
                                        <div class="text-muted fs-8">dans unigraph.ttl</div>
                                    </div>
                                </div>
                                <div class="col-6">
                                    <div class="demo-metric-box bg-success-subtle border border-success-subtle text-center">
                                        <div class="text-success fs-8 text-uppercase fw-semibold">Après Inférence</div>
                                        <div class="fs-4 fw-bold text-success">${d.after_count}</div>
                                        <div class="text-success fs-8">+${d.inferred_count} nouveaux</div>
                                    </div>
                                </div>
                            </div>

                            <details class="fs-8">
                                <summary class="text-primary fw-semibold cursor-pointer">Voir 5 triplets déduits en exemple</summary>
                                <div class="table-responsive mt-2">
                                    <table class="table table-sm table-bordered mb-0 font-monospace fs-8">
                                        <thead class="table-light">
                                            <tr><th>Sujet</th><th>Prédicat</th><th>Objet</th></tr>
                                        </thead>
                                        <tbody>
                                            ${d.sample_triples.map(t => `
                                                <tr>
                                                    <td class="text-truncate" style="max-width: 140px;" title="${t.subject}">${t.subject.split('/').pop()}</td>
                                                    <td class="text-success fw-semibold">${t.predicate}</td>
                                                    <td class="text-truncate" style="max-width: 140px;" title="${t.object}">${t.object.split('/').pop()}</td>
                                                </tr>
                                            `).join("")}
                                        </tbody>
                                    </table>
                                </div>
                            </details>
                        </div>
                    </div>
                </div>
            `).join("");
        }
    } catch (err) {
        container.innerHTML = `<div class="col-12 text-center text-danger py-4">Erreur : ${err.message}</div>`;
    }
}

// 6. API Tester
async function testApiEndpoint(route) {
    const modal = new bootstrap.Modal(document.getElementById("apiModal"));
    document.getElementById("apiModalTitle").textContent = `GET ${route}`;
    document.getElementById("apiModalBody").textContent = "Chargement en cours...";
    modal.show();

    try {
        const resp = await fetch(route);
        const json = await resp.json();
        document.getElementById("apiModalBody").textContent = JSON.stringify(json, null, 2);
    } catch (err) {
        document.getElementById("apiModalBody").textContent = `Erreur : ${err.message}`;
    }
}

async function testSparqlPost() {
    const modal = new bootstrap.Modal(document.getElementById("apiModal"));
    document.getElementById("apiModalTitle").textContent = "POST /api/sparql/execute";
    document.getElementById("apiModalBody").textContent = "Exécution de la requête test...";
    modal.show();

    const samplePayload = {
        query: "PREFIX unigraph: <https://unigraph.org/schema#>\nSELECT ?dept ?name WHERE { ?dept a unigraph:Department ; foaf:name ?name } LIMIT 3",
        use_inferred: false
    };

    try {
        const resp = await fetch("/api/sparql/execute", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(samplePayload)
        });
        const json = await resp.json();
        document.getElementById("apiModalBody").textContent = JSON.stringify(json, null, 2);
    } catch (err) {
        document.getElementById("apiModalBody").textContent = `Erreur : ${err.message}`;
    }
}
