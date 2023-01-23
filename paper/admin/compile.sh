#!/bin/bash

latex -interaction=nonstopmode cover_letter
pdflatex -interaction=nonstopmode cover_letter

rm *.aux *.log *.out *.synctex.gz *.dvi
