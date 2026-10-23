chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "analyze_job") {
        fetch("https://statewide-consistent-retreat-oak.trycloudflare.com/analyze", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ job_text: request.text })
        })
            .then(res => res.json())
            .then(data => sendResponse({ success: true, data: data }))
            .catch(err => sendResponse({ success: false, error: err.message }));

        return true;
    }
});
