function performAnalysis() {
    const sentence = document.getElementById("sentenceInput").value.trim();
    if (!sentence) return;

    fetch("/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sentence: sentence })
    })
    .then(response => response.json())
    .then(data => {
        displayStats(data.stats);
        displayTable(data.analysis);
    })
    .catch(err => console.error("Error during search propagation:", err));
}

function displayStats(stats) {
    document.getElementById("statsPanel").style.display = "flex";
    document.getElementById("statTotal").innerText = stats.total;
    document.getElementById("statMatched").innerText = stats.matched;
    document.getElementById("statUnmatched").innerText = stats.unmatched;
}

function displayTable(analysis) {
    const table = document.getElementById("resultsTable");
    const tbody = document.getElementById("resultsBody");
    tbody.innerHTML = "";

    if (analysis.length === 0) {
        table.style.display = "none";
        return;
    }

    table.style.display = "table";

    analysis.forEach((item, index) => {
        if (item.matches.length === 0) {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td><strong>${item.token}</strong></td>
                <td><span class="badge danger">Absent</span></td>
                <td colspan="5" style="color: #a0aec0; font-style: italic;">Aucune correspondance dans le dictionnaire</td>
            `;
            tbody.appendChild(row);
        } else {
            item.matches.forEach((match, matchIdx) => {
                const row = document.createElement("tr");
                const isFirst = (matchIdx === 0);
                
                row.innerHTML = `
                    <td>${isFirst ? `<strong>${item.token}</strong>` : ""}</td>
                    <td>${isFirst ? `<span class="badge success">Trouvé</span>` : ""}</td>
                    <td style="color: #2b6cb0; font-weight: bold;">${match.headword || ""}</td>
                    <td><code>${match.root || ""}</code></td>
                    <td><span style="font-style: italic; color: #4a5568;">${match.pos || "n/a"}</span></td>
                    <td>${match.french_meanings ? match.french_meanings.slice(0, 2).join(" ; ") : "Voir détails"}</td>
                    <td><button class="toggle-btn" onclick="toggleRowExpansion('exp-${index}-${matchIdx}')">Déplier</button></td>
                `;
                tbody.appendChild(row);

                const expandedRow = document.createElement("tr");
                expandedRow.id = `exp-${index}-${matchIdx}`;
                expandedRow.style.display = "none";
                expandedRow.className = "row-expanded";
                
                let sensesHtml = match.senses.map(s => `<li>${s}</li>`).join("");
                let notesHtml = match.notes.map(n => `<li>${n}</li>`).join("");

                expandedRow.innerHTML = `
                    <td colspan="7">
                        <div class="nested-details">
                            <strong>Entrée brute du dictionnaire :</strong>
                            <p style="background: #edf2f7; padding: 8px; border-radius: 4px; font-family: monospace;">${match.raw_entry}</p>
                            ${match.senses.length ? `<strong>Senses Découpés :</strong><ul>${sensesHtml}</ul>` : ""}
                            ${match.notes.length ? `<strong>Notes & Références Linguistiques :</strong><ul>${notesHtml}</ul>` : ""}
                        </div>
                    </td>
                `;
                tbody.appendChild(expandedRow);
            });
        }
    });
}

function toggleRowExpansion(id) {
    const target = document.getElementById(id);
    if (target.style.display === "none") {
        target.style.display = "table-row";
    } else {
        target.style.display = "none";
    }
}
