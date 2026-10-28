<!-- LDS: 000.432 | Meta / Agent Skill -->
<!-- ISO: ISO/IEC 42001 §7.5, ISO 27001 §A.8 | Agent: lds-orchestrator -->
<!-- Genesis Bond: GB-2025-0524-DRH-LCS-001 -->
<!-- Temporal: origin=2026-09-18T00:00:00Z updated=2026-10-28T18:31:25Z anchor=P15055828/C459/D523 basis=OBSERVED -->

# Adapter Policy Routing Reference

## Scope
Policy-gated handoff between LuciOS intent/router flows and sovereign orchestrator API contracts.

## Recommended contract pattern
1. LuciOS executes local action.
2. LuciOS forwards execution payload to adapter endpoint in `shadow` mode by default.
3. Orchestrator evaluates policy gates and returns `accepted`, reasons, and next hook hints.
4. Enforce mode only blocks when explicitly enabled.

## Required endpoint coverage
- `POST /api/v1/adapter/gui-intent`
- `GET /api/v1/adapter/gui-intent/health`

## Policy baseline
- Allowlist by action type.
- Minimum confidence threshold.
- Source service and route provenance checks.

## Validation baseline
- Unit test for accepted payload.
- Unit test for denied payload path.
- Compile checks on changed modules.
