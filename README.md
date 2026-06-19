# GovSwarm V2

> **Enterprise-Grade Security Intelligence Dashboard**  
> A real-time, AI-driven threat intelligence platform powered by a 4-agent autonomous development pipeline and a premium voice-enabled HUD.

---

## 📋 Table of Contents
- [Overview](#overview)
- [Technical Architecture](#technical-architecture)
- [Core Features](#core-features)
- [Installation](#installation)
- [Environment Setup](#environment-setup)
- [Execution](#execution)
- [Usage](#usage)
- [License](#license)
- [Contributing](#contributing)

---

## Overview

GovSwarm V2 is a cutting-edge security operations dashboard that fuses live telemetry, AI-powered analytics, and an immersive voice-controlled interface to deliver actionable intelligence for threat hunting, compliance monitoring, and incident response.

Built with a modular **4-Agent Pipeline** (Planner → Coder → Tester → Reviewer), the system continuously evolves its own capabilities while providing analysts with a **single-screen 100vh Tactical HUD** that fuses metrics, stream logs, and a dynamic forensic orb.

---

## Technical Architecture

### 4-Agent Autonomous Pipeline

| Agent | Responsibility | Tools Employed |
|-------|----------------|----------------|
| **Planner** | Transforms feature requests into detailed specifications (`.pipeline/spec.md`) | `Read`, `Grep`, `Glob`, `Write` |
| **Coder** | Implements the spec, writes minimal, clean code | `Read`, `Write`, `Edit`, `Grep`, `Glob`, `Bash` |
| **Tester** | Runs static/dynamic tests, validates fixes, ensures zero regressions | Custom test suites + `tsc --noEmit` |
| **Reviewer** | Performs final code review, ensures adherence to UI/UX guidelines (`ui-ux-rules.md`) | `Read` + comparison against spec/changes |

The pipeline is orchestrated via the `/ship` skill, which executes the four stages sequentially, producing immutable artifacts in `.pipeline/` (`spec.md`, `changes.md`, `test-results.md`, `review.md`).

### Technology Stack

- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS, Lucide Icons, Web Speech API
- **Backend**: Node.js (Express), TypeScript, Crypto FS logging
- **Communication**: REST/JSON endpoints (`/metrics`, `/api/v1/*`)
- **State Management**: React `useState`/`useEffect` with centralized telemetry
- **Animations**: CSS keyframes (`spinCW`, `pulseNeon`, `blink`, etc.) for neon‑glass aesthetic

---

## Core Features

### 🖥️ Premium 100vh Tactical HUD
- Single‑screen viewport (`height: 100vh`) via CSS Grid (`auto 1fr auto`) + Flex three‑column layout
- **Left Column**: Live Telemetry Logging & Metrics Matrix (Active Nodes, Alerts, Shield, Pending Reviews)
- **Center Column**: Dynamic Forensic Orb (nesting rings, pulsar core, optional frozen‑asset overlay)
- **Right Column**: Operator Hub (Decision Intelligence, Document Vault, Compliance Mandate, Enforcement Trigger)

### 🎙️ Voice & Speech Synthesis Sync
- Web Speech API (`SpeechRecognition`) for hands‑free vendor selection
- Real‑time sync: spoken command → state update → immediate backend telemetry fetch
- Fallback to manual dropdown & CLI input (`/scan`, `help`, `clear`)

### 📜 Live Telemetry Logging
- Persistent `security-audit.log` on the backend (timestamp, vendor, frozen flag, metrics)
- Frontend stream console with scroll‑auto‑follow, severity‑based coloring, and scanline overlay
- One‑click **Export Logs** (`.txt`) for offline analysis

### 🗂️ Admin Document Vault
- Interactive grid inside the Operator Hub showing compliance documents (PDF, JSON)
- Drag‑and‑drop‑ready placeholder for **Upload New Document** (simulated)
- Visual feedback via Lucide icons (`Upload`, `Activity`) and cyan accents

### ➕ Add Organization / Vendor
- Neon‑styled modal form (Name, Risk Score 0‑100, Compliance Status)
- Immediate addition to in‑memory `vendorDatabase` and fallback metrics
- Triggers refresh of all dashboard widgets

### 🚨 Critical Alerts & Notifications
- Blinking `[ASSETS FROZEN]` overlay when `metrics.frozen === true`
- Red toast banner for high‑risk entities (`riskScore > 70`)
- Modal escalation banner for enforcement actions

### 💻 Developer Experience
- Zero‑TypeScript‑error guarantee (`tsc --noEmit` passes)
- Pre‑commit UI/UX gate: every frontend change must consult `.claude/docs/ui-ux-rules.md`
- Fully typed backend‑frontend contract (LiveMetrics interface)

---

## Installation

### Prerequisites
- **Node.js** >= 18.x (LTS)
- **npm** >= 9.x (or Yarn/pnpm)
- **Git** (for cloning)

### Clone the Repository
```bash
git clone https://github.com/Anubhav1451/GovSwarm.git
cd GovSwarm
```

### Install Dependencies
```bash
# Backend (root) & Frontend (frontend/) are both npm workspaces
npm install
```

---

## Environment Setup

The project runs with zero required environment variables for local development.  
All configuration is baked into the source (API base `http://localhost:8000`).

If you wish to customize:

1. Create a `.env` file in the root (optional) with:
   ```env
   PORT=8000
   API_BASE=http://localhost:8000/api/v1
   ```
2. The backend reads `process.env.PORT`; the frontend uses the constant `API_BASE` (edit `src/App.tsx` if needed).

---

## Execution

### 1. Start the Backend Server
```bash
# From project root
npm run start:dev
```
or manually:
```bash
node backend/src/main.ts
```
The server will listen on **http://localhost:8000** and log:
```
🚀 GovSwarm V2 Production Core Engine securely running on port 8000
```

### 2. Start the Frontend Dashboard
```bash
# From project root
npm run dev
```
or manually:
```bash
cd frontend
npm run dev
```
The Vite dev server will be available at **http://localhost:5173** (default).

### 3. Optional: Run the Full 4‑Agent Pipeline
To simulate an autonomous feature addition:
```bash
npx claude-code -skill ship "Add a second mock vendor named 'SecureLogix Labs'..."
```
*(Requires Claude Code CLI with `/ship` skill enabled.)*

---

## Usage

### Dashboard Interaction
- **Vendor Selection**: Use the dropdown or speak a vendor name (e.g., “Apex Cyber Defense”).
- **Live Logs**: Stream updates in real time; click **PAUSE/RESUME** to freeze.
- **Export Logs**: Click **EXTRACT** to download `GOVSWARM_FORENSIC_LOG.txt`.
- **Add Organization**: Click the **ADD ORG** shield button → fill the modal → submit.
- **Document Vault**: View sample compliance documents; click the upload placeholder to trigger a simulated upload.
- **Enforcement**: Press **TRIGGER ENFORCEMENT REPORT DISPATCH** to issue a modal banner.

### Voice Commands
- Ensure microphone access is granted.
- Say: `"scan Apex Cyber Defense"` to switch context.
- Say: `"help"` to hear available CLI commands.
- Say: `"clear"` to wipe the stream log.

### Observing the 4‑Agent Pipeline (Developer)
All pipeline runs generate timestamped artifacts under `.pipeline/`:
- `spec.md` – feature specification
- `changes.md` – implemented file diff summary
- `test-results.md` – verification outcomes
- `review.md` – final reviewer verdict (`SHIP` or `REFINE`)

---

## License

This project is licensed under the **MIT License** – see the `LICENSE` file for details.

---

## Contributing

We welcome contributions that improve security intelligence, UI/UX, or pipeline reliability.

1. Fork the repository.
2. Create a feature branch (`git checkout -b feat/amazing-feature`).
3. Make your changes, ensuring:
   - Frontend edits comply with `.claude/docs/ui-ux-rules.md`.
   - `tsc --noEmit` yields zero errors.
   - New features are spec’d via the `/ship` skill (or manually mirror the pipeline).
4. Open a Pull Request with a clear description and reference to any related issues.

---

> **🛡️ GovSwarm V2** – Where autonomous AI meets human‑centric security operations.  
> “See the threat. Speak the response. Act with precision.”