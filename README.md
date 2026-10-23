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
  - `legitimate_fair_client`: Verified clean jobs with realistic expectations and fair pay.
- **📊 1–5 Danger Score Badge:** Injects clear visual indicators (🟢 Safe | ⚠️ Warning | 🚨 Nightmare) directly below the job title on Upwork.
- **⚡ Ultra-Fast Local CPU Inference:** Powered by **LAYA** (~35ms decision latencies on standard CPU, zero GPU requirement).
- **🔒 Privacy-First Architecture:** Keeps job analysis on your own private backend server.

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

# Install dependencies
pip install -r requirements.txt
pip install laya
```

### 3. Run the API Server

```bash
uvicorn server:app --host 0.0.0.0 --port 8000
```

The server will initialize the LAYA model in RAM and listen on `http://localhost:8000`.

To verify health:
```bash
curl http://localhost:8000/health
```

---

## 🔌 Chrome Extension Setup

1. Open Google Chrome and navigate to `chrome://extensions/`.
2. Enable **Developer mode** (toggle in the top right).
3. Click **Load unpacked**.
4. Select the `extension/` folder inside this project directory.
5. Visit any job details page on **Upwork** (e.g., `https://www.upwork.com/jobs/...`).
6. The **LAYA Radar Badge** will automatically inject right below the job title!

---

## 🧪 Running Test Cases

Run the pre-built test suite to evaluate 3 real-world job posting scenarios:

```bash
python test_cases.py
```

---

## 🌐 Public Tunneling (Cloudflare Tunnel)

If you want to access your local API server remotely or test the extension over secure HTTPS:

1. Download `cloudflared` from [Cloudflare Releases](https://github.com/cloudflare/cloudflared/releases/latest).
2. Start the tunnel in a separate terminal while `server.py` is running:

```bash
cloudflared tunnel --url http://localhost:8000
```

3. Update `extension/background.js` and `extension/manifest.json` with your generated `https://<your-subdomain>.trycloudflare.com` URL.

---

## 🧠 Model Info

- **Model:** `convaiinnovations/laya`
- **Architecture:** ModernBERT-Large (421M Parameters)
- **Task:** Non-autoregressive System 1 decision engine with calibrated probabilities.
- **Execution:** 100% CPU-compatible, single-pass decision matrix (~35ms).

---

## 📄 License

This project is open-source under the **MIT License**.

---

## 👤 Author

**Muhammad Asad**
- GitHub: [@MuhammadAsad29](https://github.com/MuhammadAsad29)
