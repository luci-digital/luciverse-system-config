# Rebuildable openEuler and Hyper-V Workflow

## Scope

This workflow builds a reproducible openEuler x86_64 installation ISO with `oemaker`, installs it into a dedicated Hyper-V VHDX, and applies the LuciVerse toolchain after first boot.

The existing `openEulerDev` VM and its OneDrive-backed checkpoint chain are not used by this workflow.

## Host assumptions

- Windows with WSL2 and Hyper-V enabled
- WSL distribution: `openEuler-24.03`
- Target architecture: `x86_64`
- Host CPU capability: AVX2; AVX-512 is not available
- Dedicated VM name: `openEulerLuciverse`
- Dedicated VM disk: `C:\Users\daryl\source\local-dev\openeuler-dev.vhdx`

## Why oemaker

`oemaker` produces ISO images. It does not directly produce a Hyper-V VHDX. The workflow is therefore:

```text
openEuler repositories
        |
        v
      oemaker
        |
        v
openEuler x86_64 standard ISO
        |
        v
Hyper-V installation into VHDX
        |
        v
LuciVerse post-install bootstrap
```

The openEuler 24.03 LTS repositories provide:

- `oemaker` 3.2.0
- `isocut` 3.2.0
- `envmaker` 3.2.0

## Build environment preparation

Run package operations as root inside WSL:

```powershell
wsl -d openEuler-24.03 -u root -- dnf --refresh distro-sync -y
wsl -d openEuler-24.03 -u root -- dnf install -y oemaker isocut envmaker
```

The installed package may require executable permissions to be restored for a non-root WSL user:

```powershell
wsl -d openEuler-24.03 -u root -- chmod -R a+rX /opt/oemaker /usr/bin/oemaker
```

Validate the tool:

```powershell
wsl -d openEuler-24.03 -- oemaker -h
```

`oemaker` requires more than 50 GB of working space. Keep its temporary and output directories inside the WSL filesystem rather than under a OneDrive-mounted path.

## Versioned build inputs

Record these values in every build log:

```sh
export OEMAKER_TYPE=standard
export OEMAKER_PRODUCT=openEuler
export OEMAKER_VERSION=24.03
export OEMAKER_RELEASE=LTS-SP1
export OEMAKER_REPO='<official-openEuler-24.03-x86_64-repository-url>'
export BUILD_ROOT="$HOME/luciverse-image-build"
export OUTPUT_ROOT="$BUILD_ROOT/output"
mkdir -p "$BUILD_ROOT" "$OUTPUT_ROOT"
```

Pin the repository URL and, where supported, mirror metadata or repository snapshots. Do not use an unrecorded `latest` repository for a release artifact.

## Base ISO build

The documented command shape is:

```sh
sudo oemaker \
  -t "$OEMAKER_TYPE" \
  -p "$OEMAKER_PRODUCT" \
  -v "$OEMAKER_VERSION" \
  -r "$OEMAKER_RELEASE" \
  -s "$OEMAKER_REPO"
```

The resulting ISO location is reported by `oemaker`; copy it into `$OUTPUT_ROOT` and record its SHA-256 digest:

```sh
find "$BUILD_ROOT" -type f -name '*.iso' -print
sha256sum "$OUTPUT_ROOT"/*.iso
```

Use the `standard` ISO for normal Hyper-V installation. Use `everything` only when an offline package repository is explicitly required; it consumes considerably more storage and build time.

## LuciVerse post-install manifest

After installing the ISO into the dedicated Hyper-V VM, install the build/runtime baseline:

```sh
sudo dnf --refresh distro-sync -y
sudo dnf install -y \
  git gcc gcc-c++ make cmake ninja-build \
  golang pkgconf-pkg-config openssl-devel libarchive-devel \
  curl wget tar gzip xz squashfs-tools \
  oemaker isocut envmaker
```

Then install xmake and clone the LuciVerse repository at a recorded commit:

```sh
curl -fsSL https://xmake.io/shget.text | bash
export PATH="$HOME/.local/bin:$PATH"

mkdir -p "$HOME/src"
cd "$HOME/src"
git clone https://github.com/luci-digital/luciverse-system-config.git
cd luciverse-system-config
git rev-parse HEAD
```

Build and test only the supported CPU variants:

```sh
go build ./...
go test ./...
xmake build luciverse_scalar
xmake build luciverse_avx2
xmake build luciverse_launcher
```

Do not require or deploy AVX-512 artifacts on the current i5-8365U host.

## Hyper-V handoff

The ISO is installed into a dedicated VM rather than converted directly to VHDX by `oemaker`.

Recommended VM settings:

```text
Name: openEulerLuciverse
Generation: 2
CPU: 4
Memory: 8 GB
Secure Boot: disabled
Network: Default Switch
Disk: C:\Users\daryl\source\local-dev\openeuler-dev.vhdx
```

After the ISO is available, use `scripts/create-openeuler-fresh-vm.ps1` with the ISO path and `-Apply`. Do not use `scripts/configure-openeuler-hyperv.ps1` for this fresh VM; that script targets the old OneDrive-backed VM.

## Rebuild contract

A rebuild is reproducible when these are recorded together:

1. openEuler release and architecture
2. oemaker package version
3. repository URLs and snapshots
4. oemaker arguments
5. post-install package manifest
6. LuciVerse Git commit
7. Highway Git commit
8. xmake and Go versions
9. ISO SHA-256 digest
10. Hyper-V VM configuration

## Validation checklist

```sh
cat /etc/os-release
uname -a
lscpu
ip -brief address
go version
xmake --version
oemaker -h
sha256sum <final-iso>
```

The final deployment acceptance test must run inside the Hyper-V VM, not only inside WSL, because WSL uses a Windows-managed kernel and does not provide full openEuler kernel/A-Tune/Apptainer parity.
sudo oemaker \
  -t standard \
  -p openEuler \
  -v 24.03 \
  -r LTS-SP1 \
  -s '<pinned-openEuler-x86_64-repository-url>'
