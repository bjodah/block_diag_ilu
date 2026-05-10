# -*- coding: utf-8 -*-
"""
block_diag_ilu is a C++ implementation of an incomplete LU factorization, ILU(0).
"""

from pathlib import Path

from ._release import __version__

from ._block_diag_ilu import (
    Compressed, Compressed_from_dense, Compressed_from_data,
    PyILU as ILU,
    PyLU as LU
)
from .datastruct import diag_data_len, alloc_compressed, get_compressed


def get_include():
    return str(Path(__file__).parent / "include")
