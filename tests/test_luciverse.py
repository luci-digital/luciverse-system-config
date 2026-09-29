"""Unit tests for the `bootstrap/luciverse` bootstrap orchestrator script.

The script file has no `.py` extension, so tests load it via importlib by path.

These tests mock network, subprocess and filesystem interactions so they run
fast and deterministically.
"""
import importlib.util
import json
import os
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest


def load_luciverse_module():
    repo_root = Path(__file__).resolve().parents[1]
    module_path = repo_root / "bootstrap" / "luciverse"
    spec = importlib.util.spec_from_file_location("luciverse", str(module_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_check_port_open_and_closed(monkeypatch):
    mod = load_luciverse_module()

    class FakeSocket:
        def __init__(self, *a, **k):
            self.timeout = None

        def settimeout(self, t):
            self.timeout = t

        def connect_ex(self, addr):
            ip, port = addr
            # treat port 22 as open, others closed
            return 0 if port == 22 else 1

        def close(self):
            pass

    monkeypatch.setattr(mod.socket, "socket", lambda *a, **k: FakeSocket())

    assert mod.LuciVerseBootstrap().check_port("192.168.1.10", 22) is True
    assert mod.LuciVerseBootstrap().check_port("192.168.1.10", 443) is False


def test_init_1password_signed_in_and_not_signed_in(monkeypatch):
    mod = load_luciverse_module()

    # Case: signed-in
    signed_out = SimpleNamespace(returncode=0, stdout=json.dumps([{"email": "me@example.com"}]))

    def fake_run_signed_in(*args, **kwargs):
        return signed_out

    monkeypatch.setattr(subprocess, "run", fake_run_signed_in)
    lb = mod.LuciVerseBootstrap()
    assert lb.init_1password() is True
    assert lb.op_authenticated is True

    # Case: not signed in (op present, but returns no accounts)
    not_signed = SimpleNamespace(returncode=0, stdout="[]")

    def fake_run_not_signed(*args, **kwargs):
        return not_signed

    monkeypatch.setattr(subprocess, "run", fake_run_not_signed)
    lb2 = mod.LuciVerseBootstrap()
    assert lb2.init_1password() is False
    assert lb2.op_authenticated is False

    # Case: op CLI missing -> FileNotFoundError
    def fake_run_missing(*a, **k):
        raise FileNotFoundError()

    monkeypatch.setattr(subprocess, "run", fake_run_missing)
    lb3 = mod.LuciVerseBootstrap()
    assert lb3.init_1password() is False


def test_discover_resources_detects_files_and_dirs(tmp_path, monkeypatch):
    mod = load_luciverse_module()

    # Create fake HOME, JAIL_DIR, LDS_DIR and CLAUDE_DIR
    fake_home = tmp_path / "home"
    fake_home.mkdir()

    fake_jail = tmp_path / "jail"
    fake_jail.mkdir(parents=True)
    # create a fake git repo inside jail
    (fake_jail / "repo1.git").mkdir()

    fake_ldsd = tmp_path / "luci-digital-library"
    fake_ldsd.mkdir()
    (fake_ldsd / "core-airgapped-lds").mkdir()
    (fake_ldsd / "comn-airgapped-lds").mkdir()

    fake_claude = tmp_path / ".claude"
    (fake_claude / "agents").mkdir(parents=True)
    # create agent md files
    (fake_claude / "agents" / "one.md").write_text("# agent")

    # create inventory and backup
    (fake_home / "cluster-bootstrap").mkdir()
    (fake_home / "cluster-bootstrap" / "inventory.yaml").write_text("inventory: true")
    backup_file = fake_home / "torch-lua50-jail-backup-20260124.tar.gz"
    backup_file.write_text("x" * 1024 * 1024)  # 1MB

    # Patch module paths
    monkeypatch.setattr(mod, "HOME", fake_home)
    monkeypatch.setattr(mod, "JAIL_DIR", fake_jail)
    monkeypatch.setattr(mod, "LDS_DIR", fake_ldsd)
    monkeypatch.setattr(mod, "CLAUDE_DIR", fake_claude)

    lb = mod.LuciVerseBootstrap()
    resources = lb.discover_resources()

    # We expect at least agents, lds (core/comn) and inventory and backup and jail
    types = {r["type"] for r in resources}
    assert "agents" in types
    assert "inventory" in types
    assert "backup" in types
    assert any(r.get("type") == "jail" for r in resources)


def test_activate_lucia_atuned_systemctl_and_atune(monkeypatch):
    mod = load_luciverse_module()

    # side_effect to emulate different subprocess.run behaviors
    def fake_run(cmd, capture_output=False, text=False, timeout=None):
        cmdstr = " ".join(cmd)
        if cmd[0] == "systemctl" and cmd[1] == "is-active":
            # Return active for 'atuned' and inactive for others
            service = cmd[2]
            if service == "atuned":
                return SimpleNamespace(returncode=0, stdout="active\n")
            return SimpleNamespace(returncode=3, stdout="inactive\n")
        if cmd[0] == "sudo" and cmd[1] == "systemctl" and cmd[2] == "start":
            # simulate successful start
            return SimpleNamespace(returncode=0, stdout=b"")
        if cmd[0] == "sudo" and cmd[1] == "atune-adm":
            return SimpleNamespace(returncode=0, stdout="profile1\nprofile2\n")
        return SimpleNamespace(returncode=1, stdout="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    lb = mod.LuciVerseBootstrap()
    active = lb.activate_lucia_atuned()
    assert active is True
    assert lb.atuned_active is True


def test_orchestrate_deployment_writes_state_and_reports(monkeypatch, tmp_path):
    mod = load_luciverse_module()

    fake_home = tmp_path / "home"
    fake_home.mkdir()
    monkeypatch.setattr(mod, "HOME", fake_home)

    lb = mod.LuciVerseBootstrap()
    # Prepare discovered info and flags
    lb.discovered = {"idrac": [{"ip": "1.2.3.4", "port": 22}], "resources": [{"type": "agents"}], "services": [], "agents": []}
    lb.op_authenticated = True
    lb.atuned_active = True

    # Make systemctl pretend 'active' for known services
    def fake_run_systemctl(cmd, capture_output=False, text=False):
        if cmd[:2] == ["systemctl", "is-active"]:
            # return active for anything
            return SimpleNamespace(returncode=0, stdout="active\n")
        return SimpleNamespace(returncode=1, stdout="")

    monkeypatch.setattr(subprocess, "run", fake_run_systemctl)

    deployment = lb.orchestrate_deployment()

    # Check state file was written
    state_file = fake_home / ".luciverse-state.json"
    assert state_file.exists()
    data = json.loads(state_file.read_text())
    assert data["genesis_bond"] == mod.GENESIS_BOND
    assert data["discovered"]["idrac"] == lb.discovered["idrac"]
