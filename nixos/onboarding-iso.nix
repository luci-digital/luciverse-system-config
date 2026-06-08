{ modulesPath, pkgs, lib, ... }:

{
  imports = [
    "${modulesPath}/installer/cd-dvd/installation-cd-base.nix"
  ];

  networking.hostName = "luciverse-onboarding";
  networking.useDHCP = false;
  networking.enableIPv6 = true;

  boot.kernelParams = [
    "console=tty0"
    "console=ttyS0,115200n8"
    "loglevel=4"
  ];

  environment.systemPackages = with pkgs; [
    bashInteractive
    curl
    git
    jq
    nix
    python3
    rsync
  ];

  services.getty.autologinUser = "root";

  isoImage.isoName = "luciverse-onboarding.iso";
  isoImage.contents = [
    {
      source = ../bootimus/bootimus.ipxe;
      target = "/bootimus/bootimus.ipxe";
    }
    {
      source = ../configs/network/bootimus-pxe.conf;
      target = "/bootimus/bootimus-pxe.conf";
    }
    {
      source = ../documentation/PXE_BOOT_RECOVERY_PROMPT.md;
      target = "/bootimus/PXE_BOOT_RECOVERY_PROMPT.md";
    }
    {
      source = ../schemas/foundationdb/hardware-ledger.schema.json;
      target = "/bootimus/schemas/foundationdb/hardware-ledger.schema.json";
    }
    {
      source = ../scripts/fdb-hardware-ledger-schema-init.py;
      target = "/bootimus/scripts/fdb-hardware-ledger-schema-init.py";
    }
  ];

  documentation.nixos.enable = false;

  system.stateVersion = lib.mkDefault "25.05";
}
