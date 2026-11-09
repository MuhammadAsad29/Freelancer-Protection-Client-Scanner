# 🛡️ Freelancer Protection Radar (Upwork Client Scanner)

> **Real-time AI-powered safety radar for freelancers on Upwork.** Scans job postings instantly using the **LAYA Decision Model (ModernBERT-Large)** to detect scams, sweatshops, micromanagers, and unpaid test demands before you waste connects.

---

## 🌟 Key Features

- **🚨 Real-Time Risk Detection:** Automatic background scanning of Upwork job postings as you browse.
- **🎯 5-Type Trap Classifier:**
  - `unrealistic_budget_sweatshop`: Tiny budget for massive scope or impossible deadlines.
  - `nightmare_micromanager`: 24/7 availability or heavy micromanagement signals.
  - `unpaid_sample_demand`: Unpaid trial tasks or free custom work demands.
  - `telegram_crypto_scam`: Off-platform communication attempts (Telegram, WhatsApp, crypto).
  - `legitimate_fair_client`: Jobs classified as having realistic expectations and fair pay.
- **📊 1–5 Danger Score Badge:** Injects clear visual indicators (🟢 Safe | ⚠️ Warning | 🚨 Nightmare) directly below the job title on Upwork.
- **⚡ Local CPU Inference:** Powered by **LAYA**; a GPU is not required.
- **🔒 Local by default:** The extension sends job text to the API at `127.0.0.1`. If you enable a public tunnel, requests are forwarded through that tunnel.

---

## 🏗️ System Architecture

```text
┌─────────────────────────┐         ┌──────────────────────────────┐
│  Upwork Job Page        │         │  FastAPI Backend             │
│  (Chrome Content Script)│         │  (server.py)                 │
└────────────┬────────────┘         └──────────────┬───────────────┘
             │                                     │
             │ Scrape Job Text                     │
             ▼                                     ▼
┌─────────────────────────┐   HTTP POST   ┌──────────────────────────────┐
│  Chrome Service Worker  ├──────────────►│  LAYA Decision Engine        │
│  (background.js)        │  /analyze     │  (engine.py / ModernBERT)    │
└────────────┬────────────┘               └──────────────┬───────────────┘
             │                                     │
             │ Render Badge                        │ Returns Risk Verdict
             ▼                                     ▼
┌─────────────────────────┐               ┌──────────────────────────────┐
│  Upwork UI Injector     │◄──────────────┤ { is_toxic, score, trap... } │
│  (styles.css + badge)   │               └──────────────────────────────┘
└─────────────────────────┘
```

---

## 🛠️ Project Structure

```text
├── engine.py           # LAYA Decision Engine wrapper & prompt logic
├── server.py           # FastAPI server exposing POST /analyze & /health
├── test_cases.py       # Test suite validating Upwork job scenarios
├── requirements.txt    # Python dependencies (PyTorch CPU, Transformers, FastAPI, Laya)
└── extension/          # Chrome Extension Manifest V3
    ├── manifest.json   # Extension manifest & host permissions
    ├── background.js   # Background service worker for API fetching
    ├── content.js      # DOM scanner & badge injector for Upwork
    └── styles.css      # Custom styling for radar safety badges
```

---

## 🚀 Getting Started

### 1. Prerequsites
- Python 3.10+
- Google Chrome or any Chromium-based browser

### 2. Backend Setup

Clone the repository and install dependencies:

```bash
git clone https://github.com/MuhammadAsad29/Freelancer-Protection-Client-Scanner.git
cd Freelancer-Protection-Client-Scanner

# Create and activate virtual environment
python -m venv .venv

# On Windows (PowerShell):
.venv\Scripts\Activate.ps1

# Install dependencies (includes LAYA)
python -m pip install -r requirements.txt
```

### 3. Run the API Server

```bash
python -m uvicorn server:app --host 127.0.0.1 --port 8000
```

The server will initialize the LAYA model in RAM and listen on `http://127.0.0.1:8000`. Keep this terminal open while using the extension.

To verify the API is ready, open `http://127.0.0.1:8000/health` in a browser or run:
```bash
curl http://127.0.0.1:8000/health
```

---

## 🔌 Chrome Extension Setup

1. Open Google Chrome and navigate to `chrome://extensions/`.
2. Enable **Developer mode** (toggle in the top right).
3. Click **Load unpacked**.
4. Select the `extension/` folder inside this project directory.
5. Start the API server using the instructions above.
6. Visit or refresh a job details page on **Upwork**. The **LAYA Radar Badge** should appear below the job title.

After changing extension files, click **Reload** for the extension at `chrome://extensions/`, then refresh the Upwork tab. You do not need to load the unpacked folder again.

---

## 🧪 Running Test Cases

Run the pre-built test suite to evaluate six sample job posting scenarios:

```bash
python test_cases.py
```

The tests load the LAYA model and may take time on the first run.

---

## 🌐 Public Tunneling (Cloudflare Tunnel)

The extension uses the local API by default; a tunnel is only needed if you want to access the API remotely or test through a public HTTPS URL. The API has no authentication, so anyone with the tunnel URL may be able to submit job text while the tunnel is running.

1. Download `cloudflared` from [Cloudflare Releases](https://github.com/cloudflare/cloudflared/releases/latest).
2. Keep the API server running and start the tunnel in a separate terminal:

```bash
cloudflared tunnel --url http://localhost:8000
```

3. Copy the generated `https://<your-subdomain>.trycloudflare.com` address. In `extension/background.js`, replace the URL in the `fetch(...)` call with that address followed by `/analyze`.
4. At `chrome://extensions/`, click **Reload** for the extension and refresh the Upwork tab. A quick-tunnel URL changes when a new tunnel is started, so update the fetch URL again if it changes.
5. Stop the tunnel when you are done testing.

---

## 🧠 Model Info

- **Model:** `convaiinnovations/laya`
- **Architecture:** ModernBERT-Large (421M Parameters)
- **Task:** Non-autoregressive System 1 decision engine with calibrated probabilities.
- **Execution:** CPU-compatible, single-pass decision matrix. Inference latency depends on the machine and model initialization.

---

## 📄 License

This project is open-source under the **MIT License**.

---

## 👤 Author

**Muhammad Asad**
- GitHub: [@MuhammadAsad29](https://github.com/MuhammadAsad29)
