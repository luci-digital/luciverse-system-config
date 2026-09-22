# iPXE Bootstrap Validation — Dell / Supermicro → luciverse-boot-3210

**Genesis Bond:** GB-2025-0524-DRH-LCS-001 @ 741 Hz
**Scope:** validate the iPXE/ProxyDHCP bootstrap in this repo as the first link in the
chain that boots `luciverse-boot-3210` on Dell and Supermicro server hardware.
**Basis:** OBSERVED (read of the artifacts below on 2026-09-21). Status tags per the
foundation discipline: **IMPLEMENTED / ASSERTED / GAP / RISK**.

## Artifacts examined

| Artifact | Role |
| --- | --- |
| `bootimus/bootimus.ipxe` | the iPXE menu served over HTTP after chainload |
| `configs/network/bootimus-pxe.conf` | dnsmasq ProxyDHCP: arch detection + `dhcp-boot` |
| `configs/network/dnsmasq.conf` | OOB (10.0.0.0/24) dnsmasq: interface bind, static hosts |
| `configs/zimaos-152/.../luciverse-pxe-http/docker-compose.yml` | the HTTP file server |
| `documentation/PXE_BOOT_RECOVERY_PROMPT.md` | the recorded Dell R730 UEFI conflict |
| `../../luciverse-boot-3210/luciboot.sh`, `README.md` | the target this must boot |

> **Headline:** the ProxyDHCP **architecture-detection tagging is essentially correct**
> and is the right approach for a mixed Dell/Supermicro UEFI fleet. But **the chain does
> not actually boot `luciverse-boot-3210`** — the iPXE menu terminates at a shell, three
> host/port values disagree across the configs, and there is **no integrity gate** on the
> fetched artifacts, which contradicts the platform's fail-closed principle (LP-B1/LP-F1).
> The bootstrap is a **working DHCP/arch-detection skeleton, not a completed boot path.**

---

## What passes

- **P-1 — Architecture detection is correct (IMPLEMENTED).**
  `bootimus-pxe.conf:83-86` matches BIOS (`client-arch,0`), UEFI x64 (`7`, `9`), and
  already-loaded iPXE (option `175`). Dell **and** Supermicro UEFI x64 both report
  `Arch:00007`, so the single `arch_efi64` path covers both vendors — no Supermicro-specific
  branch is needed for the loader selection.
- **P-2 — Boot-file precedence is ordered correctly (IMPLEMENTED).**
  `bootimus-pxe.conf:90-99` serves `bootimus.ipxe` to already-iPXE clients, `ipxe/ipxe.efi`
  to `arch_efi64 && !arch_ipxe`, `ipxe/undionly.kpxe` to `arch_bios && !arch_ipxe`, with an
  `undionly.kpxe` fallback. This is the standard two-stage chainload and is the documented
  fix for the R730 conflict.
- **P-3 — ProxyDHCP mode is preserved (IMPLEMENTED).**
  `dhcp-range=…,proxy` (`bootimus-pxe.conf:44-56`) keeps the ASUS RT-BE86U (`.254`) as the
  IP authority, satisfying the constraint in `PXE_BOOT_RECOVERY_PROMPT.md:32`.
- **P-4 — TFTP is scoped safely (IMPLEMENTED).**
  `enable-tftp` + `tftp-root=/srv/tftp` + `tftp-secure` (`bootimus-pxe.conf:32-34`).

---

## Gaps and risks (ordered by severity)

### G-1 — The menu never boots `luciverse-boot-3210` (GAP, blocking)
`bootimus/bootimus.ipxe:11-18` is the whole boot target, and it does nothing but print
"artifacts are published at `${base-url}/`" and `goto shell`. There is **no `kernel` /
`initrd` / `chain` / `sanboot` / `imgload`** command. The user-stated goal — "boot our
luciverse-boot-3210" — is therefore **not met by any line in this repo**. `luciverse-boot-3210`
boots via `luciboot.sh boot` **inside** an Apptainer SIF / OCI image
(`luciverse-boot-3210/README.md:41-62`); nothing here delivers a kernel+initrd or an ISO
that lands in that runtime. **Fix:** add a real boot item — either `sanboot` of the
onboarding ISO or `kernel`/`initrd` of a netboot image whose init runs `luciboot.sh boot`.

### G-2 — Host/port values disagree across three files (GAP, blocking)
The HTTP base URL is inconsistent, so even a corrected menu would fetch from the wrong place:

| Source | Host:port it names |
| --- | --- |
| `bootimus.ipxe:3` | `http://192.168.1.145:8000/bootimus` |
| `bootimus-pxe.conf:90` (`dhcp-boot` for iPXE) | `http://192.168.1.145:8000/bootimus/bootimus.ipxe` |
| `luciverse-pxe-http/docker-compose.yml:18-21` | published port **`8742`** (→ container 8080) |
| `dnsmasq.conf:5-6,45` (commented) | `http://10.0.0.1:8000/bootimus/…` on the OOB net |

The `:8000` server that `dhcp-boot` and the menu assume is **not** the `:8742` static file
server in the compose file, and the OOB path uses `10.0.0.1` while the menu hardcodes
`192.168.1.145`. **Fix:** pick one server + port, express it as a single variable
(dnsmasq option 210 / an iPXE `${next-server}` derivation), and delete the divergent copies.

### G-3 — No integrity gate on fetched artifacts (RISK, high — violates LP-F1/LP-B1)
The chainload and every artifact fetch are plain **HTTP with no verification**
(`bootimus.ipxe:3,12`; `bootimus-pxe.conf:90-99`). A sovereign, fail-closed platform must
not execute an unverified boot artifact: iPXE supports `imgverify` (code-signed images) and
per-file digests. Right now the very first link in the provenance chain — before the 3210
crypto gate ever runs (`luciboot.sh:125-138`) — is unauthenticated and fail-**open**. This is
the same defect class as **FO-10** (`lucitrust_bridge.lua`) at the network-boot layer.
**Fix:** build iPXE with a trusted CA baked in, `imgverify` the next stage, and pin a BLAKE3/
sha256 of the ISO/kernel that the DAGwood VCS already computes for it.

### G-4 — Referenced loader binaries are absent and unmanaged (GAP)
`dhcp-boot` references `ipxe/ipxe.efi` and `ipxe/undionly.kpxe` under `/srv/tftp`
(`bootimus-pxe.conf:93-99`), but `bootimus/` contains **only** `bootimus.ipxe` — no binaries,
no build recipe, no checksum. The bootstrap is not reproducible from the repo. **Fix:** add a
pinned `ipxe` build (or checked-in, checksummed binaries) and a `justfile`/`make` target that
stages them into `tftp-root`.

### G-5 — Interface / network binding is contradictory (RISK)
`dnsmasq.conf:95-96` binds `interface=enp0s31f6` (with `bind-interfaces`, `port=0` → DNS off),
while `bootimus-pxe.conf:18` comments `interface=enp12s0 (10.0.0.1)` and
`PXE_BOOT_RECOVERY_PROMPT.md:24` says dnsmasq is "strictly bound to `enp0s31f6`". Three
statements, two interfaces. On the wrong NIC the ProxyDHCP offer never reaches the servers.
**Fix:** state the boot NIC once and assert it (a preflight that fails if the bound iface has
no carrier / wrong subnet).

### G-6 — No Supermicro fleet entries or BMC/Redfish path (GAP, vendor coverage)
`dnsmasq.conf:62-69` reserves only Dell R210 II (iDRAC6) and TrueNAS; `NETWORK_REFERENCE.md`
lists `supermicro-gpu-1` at `192.168.1.170` on the **LAN**, not the OOB PXE net, with **no
static reservation and no BMC entry**. Loader selection works for Supermicro (see P-1), but
there is no remote virtual-media / one-time-`PXE`-boot automation (Dell iDRAC Redfish or
Supermicro Redfish/`SUM`) to *trigger* a netboot unattended. **Fix:** add Supermicro OOB
reservations and a Redfish `Boot Once → Pxe` step per vendor if hands-off provisioning is
intended.

### G-7 — Arch-8 handled inconsistently (RISK, minor)
`bootimus-pxe.conf:83-86` tags `arch_efi64` for arch `7` and `9` only. Arch `8` (EFI BC)
appears solely in the vendor-class comment block at the top of the same file
(`bootimus-pxe.conf:1-4`, `set:efi64` for arch `8`), which is a *different* tag from the
`dhcp-match` `arch_efi64` used by `dhcp-boot`. A client presenting arch `8` would fall through
to the `undionly.kpxe` fallback (BIOS) — the exact failure the R730 doc describes. **Fix:**
add `dhcp-match=set:arch_efi64,option:client-arch,8`.

---

## Provenance-chain view (why G-1/G-3 matter beyond boot)

The intended chain is: **iPXE → onboarding ISO/netboot image → `luciboot.sh boot` → 3210
crypto gate (fail-closed) → git-DAGwood VCS → Apptainer SIF over IPFS CIDv1**
(`luciverse-boot-3210/README.md:15-25`, `luciboot.sh:236-264`). The crypto gate at stage 20 is
strong and fail-closed, but it can only defend links *downstream of itself*. G-1 breaks the
chain before it starts (no boot), and G-3 leaves the first two links unauthenticated. Closing
them makes network-boot the true root of the same content-addressed provenance the rest of the
system already enforces — which is exactly the C2PA hard-binding posture the broader blueprint
adopts.

## Minimum work to make the claim true

1. **G-1 + G-2:** one real boot item in `bootimus.ipxe` fetching one agreed host:port that
   lands in `luciboot.sh boot`.
2. **G-3:** `imgverify` + a pinned BLAKE3/sha256 on the next stage.
3. **G-4:** reproducible, checksummed iPXE binaries staged into `tftp-root`.
4. **G-5/G-7:** assert the boot NIC; add arch-8.
5. **G-6:** Supermicro OOB reservations (+ optional Redfish trigger) if provisioning is hands-off.

Items 1–3 are the blocking set; a Dell/Supermicro server cannot today boot `luciverse-boot-3210`
from this bootstrap without them.

---

## Resolution — P1 (2026-09-21)

Applied to close the blocking set and the cheap wins:

- **G-1 (RESOLVED):** `bootimus.ipxe` now has a real `:boot` item that `imgfetch`es the onboarding
  ISO and `sanboot`s it (which lands in the NixOS onboarding image → `luciboot.sh boot`). It no
  longer dead-ends at a shell.
- **G-3 (RESOLVED, fail-closed):** boot is gated by `imgverify onboarding.iso latest.iso.sig`.
  Every failure path (fetch/verify/boot) refuses to boot and drops to the operator shell — the
  first link is now fail-*closed*. The iPXE binary must be built with the Genesis-Bond
  code-signing root (`make … TRUST=gb-codesign-ca.pem`), and `just iso-stage` now **requires**
  signing the ISO (`openssl cms` → `latest.iso.sig`); an unsigned ISO is never published.
- **G-7 (RESOLVED):** `bootimus-pxe.conf` now tags arch `8` as `arch_efi64` alongside `7` and `9`.
- **G-6 (PARTIAL):** `dnsmasq.conf` carries a Supermicro OOB-reservation + Redfish one-time-PXE
  **template** (commented, no placeholder MACs). Fill real MACs to complete.
- **G-2 (CLARIFIED):** the authoritative HTTP path is `:8000` (the menu, `dhcp-boot`, and
  `just iso-serve` all agree). The `:8742` CasaOS `luciverse-pxe-http` app is a separate ZimaOS
  deployment, not the ProxyDHCP boot server — noted, not a live contradiction on the boot path.
- **G-4 / G-5 (OPEN):** reproducible/checksummed iPXE binaries in `tftp-root`, and asserting the
  bound boot NIC, are still to do (not blocking a manual boot).

**Still required for a green P1 gate:** the operator must (a) build iPXE with the Genesis-Bond
trust root, (b) provide the signing key/cert (`GB_SIGN_*`), and (c) verify one Dell **and** one
Supermicro node boot the verified ISO end-to-end. The repo side of G-1/G-3/G-7 is done.
