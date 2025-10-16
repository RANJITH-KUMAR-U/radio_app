// static/script.js - FIXED VERSION

// === MRI/Images Preview ===
document.getElementById("mri").addEventListener("change", function() {
    const previewDiv = document.getElementById("previewImages");
    previewDiv.innerHTML = "";
    
    Array.from(this.files).forEach(file => {
        if (!file.type.match('image.*')) return;
        
        const reader = new FileReader();
        reader.onload = e => {
            const img = document.createElement("img");
            img.src = e.target.result;
            img.alt = file.name;
            previewDiv.appendChild(img);
        };
        reader.readAsDataURL(file);
    });
});

// === Form Submission & Analysis ===
document.getElementById("uploadForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    
    console.log("🚀 Starting analysis...");

    const formData = new FormData();
    const fileFields = ["structured", "genomics", "pathology", "mri"];
    
    fileFields.forEach(fieldName => {
        const files = document.getElementById(fieldName).files;
        for (let i = 0; i < files.length; i++) {
            formData.append(fieldName, files[i]);
        }
    });

    const resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = `
        <div class="result-card">
            <h3><i class="fa-solid fa-spinner fa-spin"></i> Analyzing Medical Data...</h3>
            <p>Processing multi-modal data fusion. This may take a few moments.</p>
        </div>
    `;

    try {
        console.log("📤 Sending request to server...");
        const response = await fetch("/upload", { 
            method: "POST", 
            body: formData 
        });
        
        console.log("📥 Received response:", response);
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        
        const data = await response.json();
        console.log("📊 Analysis results:", data);

        if (data.status === "ok" || data.status === "success") {
            displayResults(data.results, resultsDiv);
        } else {
            showError(data.message || 'Analysis failed', resultsDiv);
        }
    } catch (err) {
        console.error("❌ Analysis error:", err);
        showError(err.message, resultsDiv);
    }
});

function displayResults(results, container) {
    container.innerHTML = "";
    
    if (!results || results.length === 0) {
        container.innerHTML = `
            <div class="result-card">
                <h3><i class="fa-solid fa-exclamation-triangle"></i> No Results</h3>
                <p>No patient data was processed. Please check your input files.</p>
            </div>
        `;
        return;
    }
    
    results.forEach((result, idx) => {
        const card = document.createElement("div");
        card.className = "result-card";
        
        const analysis = result.analysis || {};
        const fused = result.fused || {};
        const patientId = result.patient_id || `Patient_${idx + 1}`;
        
        const riskPercent = Math.round((analysis.probability || 0) * 100);
        const riskLevel = analysis.risk_level || "UNKNOWN";
        
        let riskColor = "#00ff00";
        if (riskPercent > 70) riskColor = "#ff0000";
        else if (riskPercent > 40) riskColor = "#ffa500";

        card.innerHTML = `
            <h3><i class="fa-solid fa-user-doctor"></i> Patient: ${patientId}</h3>
            <div class="risk-bar">
                <div class="risk-fill" style="width:${riskPercent}%; background: ${riskColor}">
                    ${riskPercent}%
                </div>
            </div>
            <p><strong>Risk Level:</strong> ${riskLevel}</p>
            
            <div class="analysis-section">
                <h4><i class="fa-solid fa-diagnoses"></i> Diagnoses</h4>
                <ul>
                    ${(analysis.diagnoses || []).map(d => `
                        <li><strong>${d.condition || 'Unknown'}:</strong> 
                        ${Math.round((d.confidence || 0) * 100)}% confidence
                        ${d.evidence ? `<br><small>${d.evidence}</small>` : ''}
                        </li>
                    `).join('')}
                </ul>
            </div>

            ${(analysis.anomalies || []).length > 0 ? `
            <div class="anomaly-section">
                <h4><i class="fa-solid fa-exclamation-triangle"></i> Anomalies Detected</h4>
                <ul>
                    ${analysis.anomalies.map(anomaly => `<li>${anomaly}</li>`).join('')}
                </ul>
            </div>
            ` : ''}

            <div class="recommendation-section">
                <h4><i class="fa-solid fa-lightbulb"></i> Recommendations</h4>
                <ul>
                    ${(analysis.recommendations || []).map(rec => `<li>${rec}</li>`).join('')}
                </ul>
            </div>

            <div class="charts-container">
                <div>
                    <h5>Tumor Size (cm)</h5>
                    <canvas id="tumorChart_${idx}" width="200" height="150"></canvas>
                </div>
                <div>
                    <h5>Growth Rate</h5>
                    <canvas id="growthChart_${idx}" width="200" height="150"></canvas>
                </div>
            </div>

            <button class="download-btn"><i class="fa-solid fa-download"></i> Download Full Report</button>
        `;

        container.appendChild(card);

        // Create charts
        createTumorChart(`tumorChart_${idx}`, fused.tumor_size_cm || 0);
        createGrowthChart(`growthChart_${idx}`, fused.growth_rate || 0);

        // Download button
        const btn = card.querySelector(".download-btn");
        btn.addEventListener("click", () => downloadReport(result, patientId));

        // Highlight anomalies
        if ((analysis.anomalies || []).length > 0) {
            card.style.border = "2px solid #ff4444";
            card.style.boxShadow = "0 0 20px #ff4444";
        }
    });
}

function createTumorChart(canvasId, tumorSize) {
    try {
        new Chart(document.getElementById(canvasId), {
            type: 'bar',
            data: {
                labels: ['Size'],
                datasets: [{
                    label: 'Tumor Size (cm)',
                    data: [tumorSize],
                    backgroundColor: 'rgba(0, 255, 255, 0.6)',
                    borderColor: '#0ff',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: false,
                plugins: { legend: { display: false } },
                scales: { y: { beginAtZero: true } }
            }
        });
    } catch (error) {
        console.error("Chart error:", error);
    }
}

function createGrowthChart(canvasId, growthRate) {
    try {
        new Chart(document.getElementById(canvasId), {
            type: 'line',
            data: {
                labels: ['Rate'],
                datasets: [{
                    label: 'Growth Rate',
                    data: [growthRate],
                    backgroundColor: 'rgba(255, 100, 100, 0.3)',
                    borderColor: 'rgba(255, 0, 0, 0.8)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: false,
                plugins: { legend: { display: false } },
                scales: { y: { beginAtZero: true } }
            }
        });
    } catch (error) {
        console.error("Chart error:", error);
    }
}

function downloadReport(result, patientId) {
    const reportData = {
        patient_id: patientId,
        analysis: result.analysis,
        fused_data: result.fused,
        timestamp: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], { 
        type: "application/json" 
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `medifusion_report_${patientId}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function showError(message, container) {
    container.innerHTML = `
        <div class="result-card">
            <h3><i class="fa-solid fa-times-circle"></i> Analysis Error</h3>
            <p>${message}</p>
            <p><small>Check console for details and ensure the server is running.</small></p>
        </div>
    `;
}

// Add styles
const additionalStyles = `
    .analysis-section, .anomaly-section, .recommendation-section {
        margin: 15px 0;
        padding: 15px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
    }
    .anomaly-section { border-left: 4px solid #ff4444; }
    .analysis-section ul, .anomaly-section ul, .recommendation-section ul {
        padding-left: 20px;
    }
    .analysis-section li, .anomaly-section li, .recommendation-section li {
        margin: 8px 0;
    }
    .charts-container {
        display: flex;
        gap: 20px;
        margin: 20px 0;
        border-top: 1px solid #0ff;
        padding-top: 15px;
    }
`;

const styleSheet = document.createElement("style");
styleSheet.innerText = additionalStyles;
document.head.appendChild(styleSheet);

console.log("✅ MediFusion JavaScript loaded successfully!");