# LuciVerse Onboarding ISO Workflow

This repository now carries the operator-facing automation for the custom NixOS onboarding ISO.

## What the workflow covers

- A reproducible NixOS ISO build target in [`nixos/onboarding-iso.nix`](/Users/daryl/Documents/lucia_tooling_omzsh-master/private/luciverse-system-config/nixos/onboarding-iso.nix)
- A `justfile` entry point for build, stage, deploy, and serve tasks
- A Bootimus iPXE menu in [`bootimus/bootimus.ipxe`](/Users/daryl/Documents/lucia_tooling_omzsh-master/private/luciverse-system-config/bootimus/bootimus.ipxe)
- A FoundationDB hardware ledger schema for indexing hardware issue manifests and Hedera sequence logs

## Build

```bash
just iso-build
```

This uses `nix-build '<nixpkgs/nixos>'` with the local NixOS module to build the onboarding ISO.

## Stage

```bash
just iso-stage
```

The stage step copies the ISO into `dist/bootimus/`, publishes a `latest.iso` symlink, and drops the iPXE menu and PXE config alongside it.

## Deploy

```bash
just iso-deploy
```

Deploy is the same as stage, but it is the operator-facing command the transcript asked for: build the image, publish it, and make the boot assets available in one step.

## Serve

```bash
just iso-serve
```

This starts a local HTTP server on port `8000` rooted at `dist/`, so the Bootimus menu remains available at `http://192.168.1.145:8000/bootimus/bootimus.ipxe`.

## FoundationDB

```bash
just fdb-ledger-verify
just fdb-ledger-init
just fdb-ledger-index hardware_dir=hardware hedera_log_dir=hedera-logs
```

The schema uses these namespaces:

- `luciverse/hardware/schema`
- `luciverse/hardware/issued`
- `luciverse/hardware/artifacts`
- `luciverse/hardware/hedera`
- `luciverse/hardware/indexes`

## Operator notes

- The PXE config in [`configs/network/bootimus-pxe.conf`](/Users/daryl/Documents/lucia_tooling_omzsh-master/private/luciverse-system-config/configs/network/bootimus-pxe.conf) already serves `ipxe/ipxe.efi` for UEFI x64 clients and the Bootimus menu for iPXE clients.
- The menu script is intentionally small: it confirms the publish URL and gives the operator a controlled path to the staged ISO artifact.
- The hardware ledger script supports both static schema verification and live FoundationDB indexing.
