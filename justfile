set shell := ["bash", "-euo", "pipefail", "-c"]

default: help

nixos_config := "nixos/onboarding-iso.nix"
iso_build_link := "result/onboarding-iso"
iso_name := "luciverse-onboarding.iso"
publish_dir := "dist"
artifact_dir := "dist/bootimus"
bootimus_menu := "bootimus/bootimus.ipxe"
dnsmasq_config := "configs/network/bootimus-pxe.conf"
schema_script := "scripts/fdb-hardware-ledger-schema-init.py"

help:
    @just --list

iso-build:
    nix-build '<nixpkgs/nixos>' \
      -I nixos-config={{nixos_config}} \
      -A config.system.build.isoImage \
      --out-link {{iso_build_link}}

iso-stage: iso-build
    @mkdir -p {{artifact_dir}}
    @iso_path="$$(find -L {{iso_build_link}} -type f -name '*.iso' | head -n1)"; \
      test -n "$$iso_path"; \
      cp "$$iso_path" "{{artifact_dir}}/{{iso_name}}"; \
      ln -sf "{{iso_name}}" "{{artifact_dir}}/latest.iso"; \
      cp "{{bootimus_menu}}" "{{artifact_dir}}/bootimus.ipxe"; \
      cp "{{dnsmasq_config}}" "{{artifact_dir}}/bootimus-pxe.conf"; \
      sha256sum "{{artifact_dir}}/{{iso_name}}" > "{{artifact_dir}}/{{iso_name}}.sha256"

iso-deploy: iso-stage
    @printf '%s\n' "ISO staged in {{artifact_dir}}"

iso-serve:
    python3 -m http.server 8000 --directory {{publish_dir}}

fdb-ledger-verify:
    python3 {{schema_script}} verify

fdb-ledger-init:
    python3 {{schema_script}} init

fdb-ledger-index hardware_dir="hardware" hedera_log_dir="hedera-logs":
    python3 {{schema_script}} index \
      --hardware-dir {{hardware_dir}} \
      --hedera-log-dir {{hedera_log_dir}}

pxe-install target="/etc/dnsmasq.d/bootimus-pxe.conf":
    sudo install -Dm 0644 {{dnsmasq_config}} {{target}}
