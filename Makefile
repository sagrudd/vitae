.PHONY: pdf pdf-in-container generate website verify render clean

DOCS := Executive_CV Executive_Portfolio Executive_Biography Cover_Letter_Template

pdf:
	mkdir -p output
	find output -type f ! -name .gitkeep -delete
	docker compose build latex
	docker compose run --rm latex sh -lc 'make pdf-in-container && cp output/*.pdf /artifacts/'

pdf-in-container: generate
	mkdir -p output build/latex
	find output -type f ! -name .gitkeep -delete
	find build/latex -type f -delete
	test -L build/latex/content || ln -s ../../content build/latex/content
	@for doc in $(DOCS); do \
	  BIBINPUTS=$(CURDIR): TEXINPUTS=style: latexmk -lualatex -interaction=nonstopmode -halt-on-error -file-line-error \
	    -outdir=build/latex src/$$doc.tex || exit 1; \
	  cp build/latex/$$doc.pdf output/$$doc.pdf; \
	done
	python3 scripts/verify.py output

generate:
	python3 scripts/generate.py

website: generate

verify:
	docker compose run --rm latex python3 scripts/verify.py /artifacts

render:
	mkdir -p tmp/pdfs
	find tmp/pdfs -type f -delete
	docker compose run --rm -v "$(CURDIR)/tmp/pdfs:/renders" latex sh -lc 'for pdf in /artifacts/*.pdf; do name=$$(basename "$$pdf" .pdf); pdftoppm -png -r 120 "$$pdf" "/renders/$$name" >/dev/null; done'

clean:
	rm -rf build site tmp/pdfs
	find output -type f ! -name .gitkeep -delete
