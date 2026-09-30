from flask import Flask, request, jsonify, render_template_string
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import uuid

# ============================================================
# CIVICFIX AI - COMPLETE PROJECT IN ONE PYTHON FILE
# Backend + Frontend + Database + Demo AI logic
# Run: python app.py
# Open: http://127.0.0.1:5000
# ============================================================

app = Flask(__name__)

UPLOAD_FOLDER = "civicfix_uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Simple in-memory database.
# Data will reset when the program is stopped.
reports = []

# Demo AI knowledge base.
# This lets you demonstrate the concept without needing a separate AI server.
AI_RULES = {
    "pothole": {
        "problem": "Pothole",
        "severity": "HIGH",
        "score": 92,
        "action": "Road repair",
        "color": "#dc2626"
    },
    "road damage": {
        "problem": "Road Damage",
        "severity": "HIGH",
        "score": 89,
        "action": "Road inspection and repair",
        "color": "#dc2626"
    },
    "garbage": {
        "problem": "Garbage Dump",
        "severity": "MEDIUM",
        "score": 68,
        "action": "Waste collection",
        "color": "#f59e0b"
    },
    "waste": {
        "problem": "Waste Dump",
        "severity": "MEDIUM",
        "score": 68,
        "action": "Waste collection",
        "color": "#f59e0b"
    },
    "water leakage": {
        "problem": "Water Leakage",
        "severity": "HIGH",
        "score": 88,
        "action": "Repair water pipeline",
        "color": "#dc2626"
    },
    "water leak": {
        "problem": "Water Leakage",
        "severity": "HIGH",
        "score": 88,
        "action": "Repair water pipeline",
        "color": "#dc2626"
    },
    "streetlight": {
        "problem": "Broken Streetlight",
        "severity": "MEDIUM",
        "score": 62,
        "action": "Electrical maintenance",
        "color": "#f59e0b"
    },
    "street light": {
        "problem": "Broken Streetlight",
        "severity": "MEDIUM",
        "score": 62,
        "action": "Electrical maintenance",
        "color": "#f59e0b"
    },
    "drainage": {
        "problem": "Drainage Problem",
        "severity": "HIGH",
        "score": 84,
        "action": "Drain cleaning / repair",
        "color": "#dc2626"
    },
    "waterlogging": {
        "problem": "Waterlogging",
        "severity": "HIGH",
        "score": 86,
        "action": "Drainage inspection",
        "color": "#dc2626"
    },
    "fallen tree": {
        "problem": "Fallen Tree",
        "severity": "HIGH",
        "score": 82,
        "action": "Remove obstruction",
        "color": "#dc2626"
    }
}


def ai_detect(description):
    """
    Demo AI classifier.
    For a real competition version, this function can later be replaced
    by YOLO/OpenCV/image classification.
    """
    text = (description or "").lower()

    for keyword, result in AI_RULES.items():
        if keyword in text:
            return {
                "problem": result["problem"],
                "severity": result["severity"],
                "score": result["score"],
                "action": result["action"],
                "confidence": 94
            }

    return {
        "problem": "Civic Issue",
        "severity": "MEDIUM",
        "score": 60,
        "action": "Manual inspection required",
        "confidence": 70
    }


def calculate_stats():
    total = len(reports)
    high = sum(1 for r in reports if r["severity"] == "HIGH")
    medium = sum(1 for r in reports if r["severity"] == "MEDIUM")
    resolved = sum(1 for r in reports if r["status"] == "Resolved")
    return {
        "total": total,
        "high": high,
        "medium": medium,
        "resolved": resolved
    }


HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CivicFix AI</title>

<style>
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: Arial, Helvetica, sans-serif;
    background: #f5f7fb;
    color: #172033;
}

header {
    background: linear-gradient(135deg, #24104f, #6d28d9);
    color: white;
    padding: 18px 5%;
    position: sticky;
    top: 0;
    z-index: 10;
    box-shadow: 0 3px 15px rgba(0,0,0,.15);
}

.nav {
    max-width: 1200px;
    margin: auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 15px;
}

.logo {
    font-size: 25px;
    font-weight: 900;
}

.logo span {
    color: #d8b4fe;
}

.nav button {
    border: 1px solid rgba(255,255,255,.5);
    background: rgba(255,255,255,.12);
    color: white;
    padding: 9px 15px;
    border-radius: 10px;
    cursor: pointer;
}

.hero {
    background: linear-gradient(135deg, #24104f, #6d28d9);
    color: white;
    padding: 70px 5% 100px;
}

.hero-inner {
    max-width: 1200px;
    margin: auto;
    display: grid;
    grid-template-columns: 1.3fr .7fr;
    gap: 40px;
    align-items: center;
}

.hero h1 {
    font-size: clamp(42px, 6vw, 72px);
    line-height: 1;
    margin-bottom: 22px;
}

.hero p {
    font-size: 20px;
    line-height: 1.6;
    color: #eee;
}

.hero-card {
    background: rgba(255,255,255,.12);
    border: 1px solid rgba(255,255,255,.25);
    border-radius: 25px;
    padding: 30px;
    text-align: center;
    backdrop-filter: blur(8px);
}

.rocket {
    font-size: 85px;
    margin-bottom: 15px;
}

.container {
    width: 90%;
    max-width: 1200px;
    margin: -45px auto 60px;
    position: relative;
}

.tabs {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-bottom: 22px;
}

.tab {
    padding: 12px 20px;
    border: 0;
    border-radius: 12px;
    cursor: pointer;
    background: white;
    color: #4b5563;
    font-weight: bold;
    box-shadow: 0 4px 15px rgba(0,0,0,.07);
}

.tab.active {
    background: #6d28d9;
    color: white;
}

.panel {
    display: none;
}

.panel.active {
    display: block;
}

.card {
    background: white;
    border-radius: 20px;
    padding: 25px;
    margin-bottom: 20px;
    box-shadow: 0 6px 25px rgba(0,0,0,.07);
}

.card h2 {
    margin-bottom: 8px;
}

.muted {
    color: #6b7280;
    margin-bottom: 20px;
}

.form-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 18px;
}

.full {
    grid-column: 1 / -1;
}

label {
    display: block;
    font-weight: bold;
    margin-bottom: 7px;
}

input, textarea, select {
    width: 100%;
    padding: 13px 14px;
    border: 1px solid #d6d9e0;
    border-radius: 10px;
    font-size: 16px;
    outline: none;
}

textarea {
    min-height: 110px;
    resize: vertical;
}

input:focus, textarea:focus, select:focus {
    border-color: #7c3aed;
}

.btn {
    background: #6d28d9;
    color: white;
    border: 0;
    padding: 14px 20px;
    border-radius: 11px;
    font-size: 16px;
    font-weight: bold;
    cursor: pointer;
}

.btn:hover {
    opacity: .9;
}

.btn.secondary {
    background: #111827;
}

.btn.green {
    background: #15803d;
}

.stats {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 15px;
}

.stat {
    background: white;
    padding: 22px;
    border-radius: 17px;
    box-shadow: 0 5px 18px rgba(0,0,0,.06);
}

.stat-number {
    font-size: 36px;
    font-weight: 900;
    margin-top: 8px;
}

.report {
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    padding: 18px;
    margin-top: 15px;
}

.report-top {
    display: flex;
    justify-content: space-between;
    gap: 15px;
    align-items: center;
}

.badge {
    display: inline-block;
    padding: 6px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: bold;
}

.high {
    background: #fee2e2;
    color: #991b1b;
}

.medium {
    background: #fef3c7;
    color: #92400e;
}

.low {
    background: #dcfce7;
    color: #166534;
}

.status {
    background: #ede9fe;
    color: #5b21b6;
}

.report p {
    margin: 7px 0;
    color: #4b5563;
}

.actions {
    margin-top: 13px;
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

.small-btn {
    border: 0;
    padding: 9px 12px;
    border-radius: 8px;
    cursor: pointer;
    background: #e5e7eb;
    font-weight: bold;
}

.empty {
    text-align: center;
    padding: 35px;
    color: #6b7280;
}

.flow {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 8px;
    align-items: center;
}

.flow-item {
    text-align: center;
    padding: 17px 8px;
    background: #f5f3ff;
    border: 1px solid #ddd6fe;
    border-radius: 13px;
    font-weight: bold;
    font-size: 13px;
}

.arrow {
    text-align: center;
    font-size: 20px;
}

.success {
    background: #ecfdf5;
    color: #065f46;
    padding: 15px;
    border-radius: 12px;
    margin-top: 15px;
    display: none;
}

footer {
    text-align: center;
    background: #111827;
    color: #d1d5db;
    padding: 30px;
}

@media(max-width: 800px) {
    .hero-inner {
        grid-template-columns: 1fr;
    }

    .form-grid {
        grid-template-columns: 1fr;
    }

    .full {
        grid-column: auto;
    }

    .stats {
        grid-template-columns: 1fr 1fr;
    }

    .flow {
        grid-template-columns: 1fr;
    }

    .arrow {
        transform: rotate(90deg);
    }
}

@media(max-width: 500px) {
    .stats {
        grid-template-columns: 1fr;
    }

    .hero {
        padding-top: 45px;
    }
}
</style>
</head>

<body>

<header>
    <div class="nav">
        <div class="logo">CIVIC<span>FIX</span> AI</div>
        <div>
            <button onclick="showTab('report')">Report Issue</button>
            <button onclick="showTab('admin')">Admin</button>
        </div>
    </div>
</header>

<section class="hero">
    <div class="hero-inner">
        <div>
            <h1>One Photo.<br>One Location.<br>One Solution.</h1>
            <p>
                CivicFix AI converts citizen-reported civic problems into
                AI-assisted, location-aware and priority-ranked complaints.
            </p>
        </div>

        <div class="hero-card">
            <div class="rocket">🏙️</div>
            <h2>Smart Civic Reporting</h2>
            <p>AI • GPS • Priority • Tracking</p>
        </div>
    </div>
</section>

<main class="container">

    <div class="tabs">
        <button class="tab active" id="tab-report" onclick="showTab('report')">
            📷 Report Problem
        </button>

        <button class="tab" id="tab-track" onclick="showTab('track')">
            🔎 Track Reports
        </button>

        <button class="tab" id="tab-admin" onclick="showTab('admin')">
            🖥️ Admin Dashboard
        </button>

        <button class="tab" id="tab-about" onclick="showTab('about')">
            💡 Innovation
        </button>
    </div>

    <!-- REPORT PANEL -->
    <section id="report" class="panel active">

        <div class="card">
            <h2>📷 Report a Civic Problem</h2>
            <p class="muted">
                Describe the issue. The demo AI will classify it and calculate a priority score.
            </p>

            <form id="reportForm">

                <div class="form-grid">

                    <div>
                        <label>Your Name</label>
                        <input id="name" required placeholder="Enter your name">
                    </div>

                    <div>
                        <label>Phone</label>
                        <input id="phone" required placeholder="10-digit mobile number">
                    </div>

                    <div class="full">
                        <label>Problem Description</label>
                        <textarea id="description" required
                        placeholder="Example: Large pothole near the college gate"></textarea>
                    </div>

                    <div>
                        <label>Location</label>
                        <input id="location" required placeholder="Example: Chittoor">
                    </div>

                    <div>
                        <label>Image</label>
                        <input id="image" type="file" accept="image/*">
                    </div>

                </div>

                <br>

                <button class="btn" type="submit">
                    🤖 Analyze & Submit
                </button>

            </form>

            <div id="success" class="success"></div>
        </div>

        <div class="card">
            <h2>How CivicFix AI works</h2>
            <br>

            <div class="flow">
                <div class="flow-item">📷<br>Photo</div>
                <div class="arrow">→</div>
                <div class="flow-item">🤖<br>AI Detection</div>
                <div class="arrow">→</div>
                <div class="flow-item">📍<br>GPS</div>
                <div class="arrow">→</div>
                <div class="flow-item">⚠️<br>Priority</div>
            </div>
        </div>

    </section>

    <!-- TRACK PANEL -->
    <section id="track" class="panel">

        <div class="card">
            <h2>🔎 Citizen Complaint Tracking</h2>
            <p class="muted">All submitted reports appear here.</p>
            <div id="trackingList"></div>
        </div>

    </section>

    <!-- ADMIN PANEL -->
    <section id="admin" class="panel">

        <div class="stats">
            <div class="stat">
                <div>Total Reports</div>
                <div class="stat-number" id="statTotal">0</div>
            </div>

            <div class="stat">
                <div>High Priority</div>
                <div class="stat-number" id="statHigh">0</div>
            </div>

            <div class="stat">
                <div>Medium Priority</div>
                <div class="stat-number" id="statMedium">0</div>
            </div>

            <div class="stat">
                <div>Resolved</div>
                <div class="stat-number" id="statResolved">0</div>
            </div>
        </div>

        <br>

        <div class="card">
            <h2>🖥️ Authority Command Center</h2>
            <p class="muted">
                Officials can inspect reports and update their status.
            </p>

            <div id="adminList"></div>
        </div>

    </section>

    <!-- ABOUT PANEL -->
    <section id="about" class="panel">

        <div class="card">
            <h2>💡 Why is CivicFix AI innovative?</h2>
            <br>

            <h3>1. AI-based issue detection</h3>
            <p class="muted">
                The system analyzes the description and identifies common civic problems.
            </p>

            <h3>2. Automatic priority</h3>
            <p class="muted">
                High-risk issues receive a higher priority score.
            </p>

            <h3>3. Duplicate grouping concept</h3>
            <p class="muted">
                Multiple citizens can report the same issue. A production version can
                use GPS and AI similarity detection to combine duplicate reports.
            </p>

            <h3>4. Citizen tracking</h3>
            <p class="muted">
                Citizens can see whether an issue is submitted, assigned,
                in progress or resolved.
            </p>

            <h3>5. Scalable architecture</h3>
            <p class="muted">
                This prototype can later connect to MongoDB, real computer vision,
                maps, SMS/WhatsApp notifications and municipal systems.
            </p>
        </div>

        <div class="card">
            <h2>🏆 Competition Demo Flow</h2>
            <br>
            <div class="flow">
                <div class="flow-item">Citizen</div>
                <div class="arrow">→</div>
                <div class="flow-item">Photo</div>
                <div class="arrow">→</div>
                <div class="flow-item">AI</div>
                <div class="arrow">→</div>
                <div class="flow-item">Authority</div>
            </div>

            <br>

            <div class="flow">
                <div class="flow-item">Worker</div>
                <div class="arrow">→</div>
                <div class="flow-item">Repair</div>
                <div class="arrow">→</div>
                <div class="flow-item">Update</div>
                <div class="arrow">→</div>
                <div class="flow-item">Resolved</div>
            </div>
        </div>

    </section>

</main>

<footer>
    <strong>CivicFix AI</strong><br>
    AI-powered civic issue reporting and prioritization prototype
</footer>

<script>
function showTab(tabName) {

    document.querySelectorAll(".panel").forEach(function(panel) {
        panel.classList.remove("active");
    });

    document.querySelectorAll(".tab").forEach(function(tab) {
        tab.classList.remove("active");
    });

    document.getElementById(tabName).classList.add("active");

    let button = document.getElementById("tab-" + tabName);
    if (button) button.classList.add("active");

    if (tabName === "track") loadReports();
    if (tabName === "admin") loadReports();
}

document.getElementById("reportForm").addEventListener("submit", async function(event) {

    event.preventDefault();

    const formData = new FormData();

    formData.append("name", document.getElementById("name").value);
    formData.append("phone", document.getElementById("phone").value);
    formData.append("description", document.getElementById("description").value);
    formData.append("location", document.getElementById("location").value);

    const image = document.getElementById("image").files[0];

    if (image) {
        formData.append("image", image);
    }

    const button = event.target.querySelector("button");
    button.disabled = true;
    button.innerText = "🤖 AI analyzing...";

    try {

        const response = await fetch("/api/reports", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            alert(data.error || "Something went wrong.");
            return;
        }

        const ai = data.ai;

        document.getElementById("success").style.display = "block";

        document.getElementById("success").innerHTML =
            "<strong>✅ Report submitted!</strong><br><br>" +
            "Complaint ID: <strong>" + data.report.id + "</strong><br>" +
            "AI detected: <strong>" + ai.problem + "</strong><br>" +
            "Confidence: <strong>" + ai.confidence + "%</strong><br>" +
            "Severity: <strong>" + ai.severity + "</strong><br>" +
            "Priority Score: <strong>" + ai.score + "/100</strong><br>" +
            "Recommended action: <strong>" + ai.action + "</strong>";

        event.target.reset();

    } catch (error) {
        alert("Server error. Make sure the Flask program is running.");
    }

    button.disabled = false;
    button.innerText = "🤖 Analyze & Submit";

    loadReports();
});


async function loadReports() {

    const response = await fetch("/api/reports");
    const data = await response.json();

    updateStats(data.stats);
    renderTracking(data.reports);
    renderAdmin(data.reports);
}


function updateStats(stats) {
    document.getElementById("statTotal").innerText = stats.total;
    document.getElementById("statHigh").innerText = stats.high;
    document.getElementById("statMedium").innerText = stats.medium;
    document.getElementById("statResolved").innerText = stats.resolved;
}


function renderTracking(reports) {

    const box = document.getElementById("trackingList");

    if (reports.length === 0) {
        box.innerHTML = '<div class="empty">No complaints submitted yet.</div>';
        return;
    }

    box.innerHTML = reports.map(function(r) {

        return `
        <div class="report">
            <div class="report-top">
                <strong>${escapeHtml(r.id)} — ${escapeHtml(r.problem)}</strong>
                <span class="badge ${r.severity === "HIGH" ? "high" : "medium"}">
                    ${escapeHtml(r.severity)}
                </span>
            </div>

            <p>📍 ${escapeHtml(r.location)}</p>
            <p>📝 ${escapeHtml(r.description)}</p>
            <p>⚠️ Priority: <strong>${r.score}/100</strong></p>
            <p>🕒 ${escapeHtml(r.created_at)}</p>
            <p>
                Status:
                <span class="badge status">${escapeHtml(r.status)}</span>
            </p>
        </div>
        `;

    }).join("");
}


function renderAdmin(reports) {

    const box = document.getElementById("adminList");

    if (reports.length === 0) {
        box.innerHTML = '<div class="empty">No complaints in the command center.</div>';
        return;
    }

    box.innerHTML = reports.map(function(r) {

        return `
        <div class="report">

            <div class="report-top">
                <strong>${escapeHtml(r.id)} — ${escapeHtml(r.problem)}</strong>

                <span class="badge ${r.severity === "HIGH" ? "high" : "medium"}">
                    ${escapeHtml(r.severity)}
                </span>
            </div>

            <p>👤 ${escapeHtml(r.name)}</p>
            <p>📞 ${escapeHtml(r.phone)}</p>
            <p>📍 ${escapeHtml(r.location)}</p>
            <p>📝 ${escapeHtml(r.description)}</p>
            <p>🤖 AI Confidence: ${r.confidence}%</p>
            <p>⚠️ Priority: <strong>${r.score}/100</strong></p>

            <p>
                Current Status:
                <span class="badge status">${escapeHtml(r.status)}</span>
            </p>

            <div class="actions">

                <button class="small-btn"
                    onclick="updateStatus('${r.id}', 'Assigned')">
                    Assign
                </button>

                <button class="small-btn"
                    onclick="updateStatus('${r.id}', 'In Progress')">
                    Start Work
                </button>

                <button class="small-btn"
                    onclick="updateStatus('${r.id}', 'Resolved')">
                    Resolve
                </button>

            </div>

        </div>
        `;

    }).join("");
}


async function updateStatus(id, status) {

    const response = await fetch("/api/reports/" + encodeURIComponent(id), {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            status: status
        })
    });

    const data = await response.json();

    if (!response.ok) {
        alert(data.error || "Could not update status.");
        return;
    }

    loadReports();
}


function escapeHtml(value) {

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


loadReports();
</script>

</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/api/reports", methods=["GET"])
def get_reports():
    return jsonify({
        "reports": reports,
        "stats": calculate_stats()
    })


@app.route("/api/reports", methods=["POST"])
def create_report():

    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    description = request.form.get("description", "").strip()
    location = request.form.get("location", "").strip()

    if not name or not phone or not description or not location:
        return jsonify({
            "error": "Please fill all required fields."
        }), 400

    ai = ai_detect(description)

    report_id = "CF-" + str(uuid.uuid4())[:6].upper()

    image_name = ""

    image = request.files.get("image")

    if image and image.filename:

        safe_name = secure_filename(image.filename)

        image_name = report_id + "_" + safe_name

        image.save(
            os.path.join(UPLOAD_FOLDER, image_name)
        )

    report = {
        "id": report_id,
        "name": name,
        "phone": phone,
        "description": description,
        "location": location,
        "problem": ai["problem"],
        "severity": ai["severity"],
        "score": ai["score"],
        "confidence": ai["confidence"],
        "action": ai["action"],
        "status": "Submitted",
        "image": image_name,
        "created_at": datetime.now().strftime("%d-%m-%Y %I:%M %p")
    }

    reports.insert(0, report)

    return jsonify({
        "message": "Report created successfully.",
        "report": report,
        "ai": ai
    })


@app.route("/api/reports/<report_id>", methods=["PUT"])
def update_report(report_id):

    data = request.get_json(silent=True) or {}
    new_status = data.get("status")

    allowed_statuses = [
        "Submitted",
        "Assigned",
        "In Progress",
        "Resolved"
    ]

    if new_status not in allowed_statuses:
        return jsonify({
            "error": "Invalid status."
        }), 400

    for report in reports:

        if report["id"] == report_id:

            report["status"] = new_status

            return jsonify({
                "message": "Status updated.",
                "report": report
            })

    return jsonify({
        "error": "Report not found."
    }), 404


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


if __name__ == "__main__":
    print("=" * 60)
    print("CIVICFIX AI - Innovation Challenge Prototype")
    print("=" * 60)
    print("Open this in your browser:")
    print("http://127.0.0.1:5000")
    print("Press CTRL+C to stop the server.")
    print("=" * 60)

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
