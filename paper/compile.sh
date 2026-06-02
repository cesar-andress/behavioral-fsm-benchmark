#!/usr/bin/env bash
# Compile EMSE manuscript locally (Springer sn-jnl class bundled in latex-class/)
set -euo pipefail
cd "$(dirname "$0")"
export TEXINPUTS="${PWD}/latex-class//:${TEXINPUTS:-}"
export BSTINPUTS="${PWD}/latex-class//:${BSTINPUTS:-}"
pdflatex -interaction=nonstopmode main.tex
if [[ -f references/references.bib ]] && grep -q '\\bibliography{' main.tex; then
  bibtex main 2>/dev/null || true
  pdflatex -interaction=nonstopmode main.tex
  pdflatex -interaction=nonstopmode main.tex
fi
echo "Output: $(pwd)/main.pdf"
