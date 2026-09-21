# Serial, offline-data paper build. Model calls and benchmark reruns are never made.
.NOTPARALLEL:
.DEFAULT_GOAL := html
export UV_CACHE_DIR := /private/tmp/ve-uv-cache
export XDG_CACHE_HOME := $(CURDIR)/.cache
export TECTONIC_CACHE_DIR := $(CURDIR)/.cache/tectonic
export MPLCONFIGDIR := $(CURDIR)/.cache/matplotlib
export PYTHONHASHSEED := 0
PYTHON := uv run --project .. --frozen --with matplotlib==3.11.2 python
PANDOC := pandoc build/paper.md --metadata-file=metadata.yaml --from=markdown+pipe_tables+footnotes --number-sections --resource-path=.

.PHONY: html pdf generate assemble check placeholders pages clean

generate:
	mkdir -p .cache/tectonic .cache/matplotlib build generated
	$(PYTHON) figures/gen_e0_tables.py
	$(PYTHON) figures/gen_implementation_tables.py
	$(PYTHON) figures/gen_judge_ladder.py
	$(PYTHON) figures/gen_system.py

assemble: generate
	python3 build.py

html: assemble
	$(PANDOC) --standalone --embed-resources --mathml --lua-filter=html-images.lua --css=style.css -o build/paper.html
	python3 verify.py --html

pdf: assemble
	$(PANDOC) --lua-filter=keep-tables.lua --pdf-engine=tectonic -o build/paper.pdf
	python3 verify.py --pdf

check: html

placeholders:
	python3 build.py --placeholders

pages:
	pdfinfo build/paper.pdf

clean:
	rm -rf build
