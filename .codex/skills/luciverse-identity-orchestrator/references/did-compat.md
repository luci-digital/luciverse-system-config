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
