#!/bin/bash
BLOCK_DIAG_ILU_LAPACK=openblas CPLUS_INCLUDE_PATH=${PREFIX}/include ${PYTHON} setup.py build
${PYTHON} setup.py build
${PYTHON} setup.py install
