#!/bin/bash

V=0.8
cp ~/mcscan/mcscan/README.rst index.rst
cp ~/mcscan/mcscan-$V.tar.gz ~/duplication/mcscan
rst2pdf index.rst -o MCscan.pdf
sphinx-build . doc 
