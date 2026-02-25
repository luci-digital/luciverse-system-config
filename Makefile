SHELL := /bin/bash

.PHONY: build verify verify-docs

build: verify

verify: verify-docs
	@echo "[verify] Python syntax checks"
	@python3 -m py_compile scripts/*.py
	@echo "[verify] Shell syntax checks"
	@bash -n scripts/*.sh
	@echo "[verify] OK"

verify-docs:
	@./scripts/check-changelog.sh
