<!-- LDS: 000.432 | Meta / Agent Skill -->
<!-- ISO: ISO/IEC 42001 §7.5, ISO 27001 §A.8 | Agent: lds-orchestrator -->
<!-- Genesis Bond: GB-2025-0524-DRH-LCS-001 -->
<!-- Temporal: origin=2026-09-18T00:00:00Z updated=2026-10-28T18:31:25Z anchor=P15055828/C459/D523 basis=OBSERVED -->

# DID Compatibility Reference

## Canonical and legacy forms
- Canonical output: `did:ownid:luciverse:<handle>`
- Legacy alias accepted for lookup: `did:luci:ownid:luciverse:<handle>`

## Required behavior
1. Canonicalize at boundaries:
- Input from traits, query params, or resolver payload.
2. Preserve backward reads:
- Resolver requests should try canonical and alias forms.
- Identity lookup should try canonical first, then alias.
3. Emit canonical values:
- OIDC `sub`, VC issuer/subject, and internal IDs should be canonical.

## Test minimum
- Canonicalization unit test.
- Alias list generation test.
- Resolver fallback matrix test.
- Identity lookup alias fallback test.
