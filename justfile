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
# Genesis-Bond code-signing material for the fail-closed boot chain (G-3).
# Override via env: GB_SIGN_CERT / GB_SIGN_KEY / GB_SIGN_CA. iso-stage FAILS if
# the ISO cannot be signed — an unsigned artifact is never published.
gb_sign_cert := env_var_or_default("GB_SIGN_CERT", "keys/gb-codesign.crt")
gb_sign_key := env_var_or_default("GB_SIGN_KEY", "keys/gb-codesign.key")
gb_sign_ca := env_var_or_default("GB_SIGN_CA", "keys/gb-codesign-ca.crt")

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
    @# FAIL-CLOSED signing (G-3): iPXE imgverify needs a detached CMS signature
    @# whose chain roots at the Genesis-Bond code-signing CA baked into ipxe.efi
    @# (make ... TRUST=gb-codesign-ca.pem). No key -> stage FAILS, nothing ships.
    @test -f "{{gb_sign_cert}}" || { echo "FAIL-CLOSED: missing {{gb_sign_cert}} (set GB_SIGN_CERT)"; exit 1; }
    @test -f "{{gb_sign_key}}"  || { echo "FAIL-CLOSED: missing {{gb_sign_key}} (set GB_SIGN_KEY)"; exit 1; }
    openssl cms -sign -binary -noattr \
      -in "{{artifact_dir}}/{{iso_name}}" \
      -signer "{{gb_sign_cert}}" -inkey "{{gb_sign_key}}" -certfile "{{gb_sign_ca}}" \
      -outform DER -out "{{artifact_dir}}/{{iso_name}}.sig"
    @ln -sf "{{iso_name}}.sig" "{{artifact_dir}}/latest.iso.sig"
    @echo "Signed {{iso_name}} -> {{iso_name}}.sig (imgverify-ready, fail-closed)"

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
