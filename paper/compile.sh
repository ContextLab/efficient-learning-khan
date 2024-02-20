#!/bin/bash

latex -interaction=nonstopmode main
bibtex main
latex -interaction=nonstopmode main
latex -interaction=nonstopmode main
latex -interaction=nonstopmode main
latex -interaction=nonstopmode main
pdflatex -interaction=nonstopmode main

latex -interaction=nonstopmode supplement
bibtex supplement
latex -interaction=nonstopmode supplement
latex -interaction=nonstopmode supplement
pdflatex -interaction=nonstopmode supplement

latexdiff old.tex main.tex > changes.tex
latex -interaction=nonstopmode changes
bibtex changes
latex -interaction=nonstopmode changes
latex -interaction=nonstopmode changes
pdflatex -interaction=nonstopmode changes3


rm *.cb* *.dvi *.log *.blg *.aux *.fff *.out

