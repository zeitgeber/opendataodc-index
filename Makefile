SHELL := /bin/bash
UV ?= /home/adi/.local/bin/uv
UV_CACHE_DIR ?= /tmp/uv-cache

.PHONY: check validate

check: validate

validate:
	UV_CACHE_DIR=$(UV_CACHE_DIR) $(UV) run python scripts/validate_index.py
