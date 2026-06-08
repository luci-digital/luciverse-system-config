# SCION Deployment Package

This document packages the SCION-related deployment changes that were split out of the live storage/network bundle and normalized for upstream review.

## What the package contains

The canonical deployment bundle is made of explicit artifacts instead of one opaque directory mount:

- `scion-config.nix`
- `generate-topology.nix`
- `docker-compose.yml`
- `deploy.sh`
- `br.toml`
- `cs.toml`
- `crypto/`
- `topology.json`
- `.env.example`

## Storage and network split

The updated bundle separates static storage artifacts from network/runtime configuration:

- Storage artifacts:
  - `crypto/` holds the SCION keys and certificate material that should remain outside source control.
  - `topology.json` is generated at deploy time and treated as a materialized artifact.
- Network/runtime configuration:
  - `scion-config.nix` derives AS and border-router values from the environment.
  - `docker-compose.yml` mounts only the required artifacts and injects the daemon address.
  - `deploy.sh` derives its own directory and regenerates `topology.json` before bringing the stack up.

## Environment contract

The deployment is driven by these environment variables:

| Variable | Purpose |
|---|---|
| `SCION_AS` | SCION AS identifier used by the topology generator |
| `SCION_BR_INTERNAL_ADDR` | Internal border-router address |
| `SCION_CONTROL_ADDR` | SCION control-service address |
| `SCION_BORDER_PUBLIC_ADDR` | Public border-router address |
| `SCION_BORDER_REMOTE_ADDR` | Remote peering address |
| `SCION_DAEMON_ADDRESS` | SCION daemon endpoint used by the gateway |
| `SCION_TOPOLOGY_OUT` | Output path for the generated topology |
| `COMPOSE_BIN` | Compose binary used by the deploy script |

## Validation

The live bundle was validated with:

```bash
bash -n deploy.sh
nix-build --no-out-link --impure generate-topology.nix
python3 -m json.tool topology.json >/dev/null
```

## Upstream alignment

The patch set is aligned with the current upstream SCION ecosystem:

- [netsec-ethz/scion](https://github.com/netsec-ethz/scion)
- [netsec-ethz/scion-apps](https://github.com/netsec-ethz/scion-apps)
- [netsec-ethz/fpki](https://github.com/netsec-ethz/fpki)
- [netsec-ethz/rains](https://github.com/netsec-ethz/rains)

The goal is to keep the deployment package reproducible, explicit, and easy to review as a GitHub patch series.
