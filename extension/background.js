chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "analyze_job") {
        fetch("http://127.0.0.1:8000/analyze", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ job_text: request.text })
        })
            .then(async res => {
                const data = await res.json();
                if (!res.ok) {
                    throw new Error(data.detail || `API returned ${res.status}`);
                }
                return data;
            })
            .then(data => sendResponse({ success: true, data: data }))
            .catch(err => sendResponse({ success: false, error: err.message }));

        return true;
    }
});
