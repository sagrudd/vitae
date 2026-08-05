.PHONY: pdf pdf-in-container generate website verify render clean cv portfolio biography docker release

DOCS := Executive_CV Executive_Portfolio Executive_Biography Cover_Letter_Template

pdf:
	mkdir -p output
	find output -type f ! -name .gitkeep -delete
	docker compose build latex
	docker compose run --rm latex sh -lc 'make pdf-in-container && cp output/*.pdf /artifacts/'

cv: docker
	docker compose run --rm latex sh -lc 'make pdf-in-container DOCS=Executive_CV && cp output/Executive_CV.pdf /artifacts/'

portfolio: docker
	docker compose run --rm latex sh -lc 'make pdf-in-container DOCS=Executive_Portfolio && cp output/Executive_Portfolio.pdf /artifacts/'

biography: docker
	docker compose run --rm latex sh -lc 'make pdf-in-container DOCS=Executive_Biography && cp output/Executive_Biography.pdf /artifacts/'

docker:
	docker compose build latex

pdf-in-container: generate
	mkdir -p output build/latex
	find output -type f ! -name .gitkeep -delete
	find build/latex -type f -delete
	test -L build/latex/content || ln -s ../../content build/latex/content
	@for doc in $(DOCS); do \
	  BIBINPUTS=$(CURDIR): TEXINPUTS=style: latexmk -silent -lualatex -interaction=nonstopmode -halt-on-error -file-line-error \
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

VERSION ?= v2026.1
release: pdf
	git tag -a "$(VERSION)" -m "Release $(VERSION)"
	git push origin main --tags
