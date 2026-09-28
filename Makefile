.PHONY: webapp-copy-check webapp-build

webapp-copy-check:
	.venv/bin/python -m webapp.vocabulary.audit --strict

webapp-build: webapp-copy-check
	uv build
