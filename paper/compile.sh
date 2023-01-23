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

rm *.cb* *.dvi *.log *.blg *.aux *.fff *.out

