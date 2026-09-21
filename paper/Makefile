# Build the VE paper. Requires pandoc and tectonic. Run from paper/: `make pdf`.
SECTIONS := $(sort $(wildcard sections/*.md))
GENERATED := generated/e0-coverage-table.md generated/e0-constructs-table.md

.PHONY: pdf tables figures placeholders pages clean

pdf: build/paper.pdf

# Tables are generated from committed data (see figures/gen_e0_tables.py). The outputs are
# committed too, so `make pdf` also works where the source branch is not available.
tables:
	python3 figures/gen_e0_tables.py

figures: figures/system.pdf

figures/system.pdf: figures/system.tex
	cd figures && tectonic system.tex

build/paper.md: $(SECTIONS) $(GENERATED) build.py
	python3 build.py

build/paper.pdf: build/paper.md metadata.yaml figures/system.pdf
	pandoc build/paper.md --metadata-file=metadata.yaml --from=markdown+pipe_tables+footnotes \
	  --pdf-engine=tectonic --resource-path=. -o build/paper.pdf

# List every result placeholder that still has to be filled.
placeholders:
	@grep -n -o "RESULT-[A-Z0-9-]*" $(SECTIONS) | sort -u -t: -k3

pages: build/paper.pdf
	@python3 -c "import re,sys; d=open('build/paper.pdf','rb').read(); print(max(int(n) for n in re.findall(rb'/Count (\d+)', d)))"

clean:
	rm -rf build
