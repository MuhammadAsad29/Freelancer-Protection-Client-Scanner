console.log("[LAYA Radar] Content script loaded on Upwork!");

function extractJobDescription() {
    const selectors = [
        '[data-test="JobDescription"]',
        '[data-test="job-description-text"]',
        '[data-qa="job-description"]',
        '.air3-card-section',
        '.job-description',
        'main p'
    ];

    for (const selector of selectors) {
        const elements = document.querySelectorAll(selector);
        for (const el of elements) {
            const text = el.innerText.trim();
            if (text.length > 60) {
                return text;
            }
        }
    }

    const allParagraphs = Array.from(document.querySelectorAll('p, div, section'));
    for (const p of allParagraphs) {
        const text = p.innerText.trim();
        if (text.length > 150 && !text.includes("Cookie") && !text.includes("Terms of Service")) {
            return text;
        }
    }

    return null;
}

function renderBadge(result, anchorElement) {
    const existingBadge = document.getElementById("laya-radar-badge");
    if (existingBadge) existingBadge.remove();

    const badge = document.createElement("div");
    badge.id = "laya-radar-badge";

    let colorClass = "laya-safe";
    let icon = "🟢";

    if (result.toxicity_score >= 4) {
        colorClass = "laya-danger";
        icon = "🚨";
    } else if (result.toxicity_score === 3) {
        colorClass = "laya-warning";
        icon = "⚠️";
    }

    badge.className = colorClass;
    badge.innerHTML = `
        <div class="laya-title">
            <span>${icon} LAYA Radar: Danger Score ${result.toxicity_score}/5</span>
            <span style="font-size: 11px; opacity: 0.7; font-weight: normal;">(Local AI Scan)</span>
        </div>
        <div class="laya-detail">
            <strong>Trap Type:</strong> ${result.trap_type.replaceAll("_", " ").toUpperCase()}<br>
            <strong>Advice:</strong> ${result.reason}
        </div>
    `;

    anchorElement.insertAdjacentElement("afterend", badge);
    console.log("[LAYA Radar] Badge successfully injected under Title!");
}

let lastScannedText = "";
let isScanning = false;

async function scanCurrentJob() {
    if (isScanning || document.getElementById("laya-radar-badge")) return;

    const titleEl = document.querySelector("h1") || document.querySelector("h2");
    if (!titleEl) return;

    const jobText = extractJobDescription();
    if (!jobText || jobText === lastScannedText) return;

    isScanning = true;
    lastScannedText = jobText;

    console.log("[LAYA Radar] Found new job text, routing through background worker...");

    chrome.runtime.sendMessage(
        { action: "analyze_job", text: jobText },
        (response) => {
            isScanning = false;
            if (response && response.success) {
                console.log("[LAYA Radar] Analysis received:", response.data);
                renderBadge(response.data, titleEl);
            }
        }
    );
}

setInterval(scanCurrentJob, 2000);
