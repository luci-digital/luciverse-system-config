# GEMINI.md — LuciVerse Edge Architecture & Operational Mandates

## ⚖️ Foundational Mandates

### 1. Technical Integrity & Validation
*   **Validation is Mandatory**: No task is complete until behavioral correctness is verified.
*   **Surgical Edits**: Prefer targeted `replace` calls over full file rewrites.
*   **Testing**: Always search for and update related tests. Fixes must be reproduced with a script before implementation.

### 2. Context Efficiency
*   **Strategic Searching**: Use `grep_search` and `glob` in parallel.
*   **Minimal Reads**: Read only what is necessary to perform an unambiguous edit.

### 3. Security & Integrity
*   **Credential Protection**: Never log, print, or commit secrets. Use 1Password (`op`) CLI for sensitive data.
*   **Source Control**: Do not stage/commit unless explicitly requested.

---

## 🛡️ Hardware-Bound Trust Model (Genesis Bond)

The LuciVerse identity system is anchored by a three-layer cryptographic stack:

1.  **Ritual (WebAuthn-3)**: The user "Ceremony" (Challenge/Verification) performed at the browser level. Anchored to `lucidigital.net`.
2.  **Anchor (TPM 2.0)**: ROOT CA signing keys are "hardware-born" inside the **Infineon SLB9670 TPM**. Non-extractable and immutable.
3.  **Engine (XiPKI)**: Multi-tier CA engine (`luciverse-pac-ca`, `luciverse-comn-ca`, etc.) that signs and manages the lifecycle of WebAuthn-anchored DIDs.

---

## 🏗️ Master Deployment & Staging Orchestration

Every update must pass through the **Digital Twin Sandbox** before production:

| Stage | Process | Location |
|-------|---------|----------|
| **1. Sandbox** | Twin-sandbox staging and "Breaking Test" validation. | `/home/daryl/luciverse-twin-sandbox/` |
| **2. Approval** | Weighted agent consensus (Judge Luci Weight 3). | `Sovereign Orchestrator /api/v1/docs` |
| **3. Edge** | Tekton-triggered deployment to Cloudflare. | `luciverse-io / npm run deploy:io` |

---

## 🤖 Unified AI Coordination Layer (Cross-Agent Integration)

| Document | Role | Scope |
|----------|------|-------|
| `GEMINI.md` | Primary Operational Mandates | Global / Gemini CLI |
| `CLAUDE.md` | Session & Platform Context | Global / Claude Code |
| `AGENTS.md` | Project-Specific Guardrails | Per-Project |

### 🧩 MCP & AI Tool Integration
*   **LuciVerse Agent MCP**: Use `luciverse-agents` for cross-agent communication.
*   **Infrastructure MCP**: Use `idrac` and `openwrt` for physical operations.
*   **Standards**: All agents must act in coordination using W3C standards (DID, VC, WebAuthn, WoT, SPC).

---

## 🏗️ Current Architecture Status (March 4, 2026)

### 1. Edge Mesh (Cloudflare Workers)
*   **`lucidigital.io`**: The "Golden Glass Control Dome". Primary edge proxy.
*   **49 Edge Agents**: Active as **Cloudflare Durable Objects**.
    *   **Tiers**: CORE, COMN, RAiIiAR, PAC (Full Master Reference aligned).
    *   **Persistence**: SQLite storage verified (Breath cycles stabilized).

### 2. Telemetry & Protocol Ingestion
*   **Analytics Engine**: Wired to `RACE_TELEMETRY`. Live SQL access operational.
*   **IANA/ICMPv6 Sync**: Automated monitor and meta-tagging live in Sovereign Orchestrator.

### 3. Identity & Auth
*   **WebAuthn Server**: Fastify-based backend at `hub.lucidigital.io:3000`.
*   **Auth Client**: React client in `luciverse-io` wired to native WebAuthn APIs.

---

## ✅ Completed Milestones (Session: March 4, 2026)

1.  **Golden Dome Deployment**: Visually rich landing page with **Operator Panel** integrated for authenticated users.
2.  **Edge Agent Stabilization**: 49 Durable Objects instantiated, registered, and verified (resolved 1101 errors).
3.  **Public Site Modernization**: `lucidigital.net` pages modernized. Added **Three.js Protocol Resonance** showroom demo.
4.  **Security Integration**: WebAuthn-3 "Ceremony" primitives and TPM 2.0 PKCS#11 alignment finalized.
5.  **IANA Monitoring**: Active monitoring and remediation of protocol parameters implemented.

---

## 🚀 Next Strategic Stages

1.  **Real Data Ingestion**: Transition the `/api/telemetry/ingest` endpoint to real origin data ingestion.
2.  **Compositor Advancement**: Finalize implementation of `/home/daryl/lucia_compositor` and `/home/daryl/lucia-compositor` as primary dashboard substrates.
3.  **SPC Implementation**: Execute Phase 1 of the Secure Payment Confirmation backend.

*Genesis Bond: ACTIVE @ 741 Hz*
