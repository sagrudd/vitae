FROM debian:12.6-slim

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    biber latexmk make poppler-utils python3 python3-pypdf python3-reportlab \
    texlive-bibtex-extra texlive-fonts-extra texlive-fonts-recommended texlive-latex-extra texlive-luatex texlive-pictures \
    && rm -rf /var/lib/apt/lists/*
RUN luaotfload-tool --update --force
# Debian's latexmk MD5 helper can fail on Docker Desktop shared filesystems.
RUN sed -i 's/\$md5->addfile(\$input);/while (<\$input>) { \$md5->add(\$_); }/' /usr/bin/latexmk
WORKDIR /work
COPY . /work
ENV HOME=/tmp TEXMFVAR=/tmp/texmf-var SOURCE_DATE_EPOCH=1785888000
CMD ["make", "pdf-in-container"]
