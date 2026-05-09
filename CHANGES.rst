v0.5.3
======
Use Cython from setup.py whenever there's a .pyx file available.

v0.5.2
======
Re-render cython sources.

v0.5.1
======
Release script was broken.

v0.5.0
======
New AnyODE interface jtimes_setup

v0.4.7
======
Previous version broken.

v0.4.6
======
No change except rerendered Cython source for PyPI distribution.

v0.4.5
======
- Cython: use language_level=3

v0.4.4
======
- Use latest AnyODE

v0.4.3
======
- update setup.py to re-run Cython when .pyx available
- update setup.py to new requirements in more recent versions of setuptools

v0.4.2
======
- Changes to setup.py

v0.4.1
======
- Fix escape sequence in setup.py

v0.4.0
======
- New v0.4 branch (new AnyODE)

v0.3.8
======
- Use latest AnyODE

v0.3.7
======
- Avoid using exceptions in program flow

v0.3.6
======
- Only require C++11
- Deprecate BLOCK_DIAG_ILU_WITH_GETRF macro

v0.3.5
======
- Require C++14 for now, rationale: Python's distutils' C++ support is truly terrible
  (CXXFLAGS not supported for starters).

v0.3.4
======
- More robust build (conda-recipe)
- Updated AnyODE

v0.3.3
======
- Fix ld in Cython wrapper

v0.3.2
======
- BlockDiagMatrix needed to inspect m_colmaj

v0.3.1
======
- Bumpy AnyODE
- Make helper functions inline (avoid multiple definition)

v0.3.0
======
- Use int throughout instead of unsigned and size_t.
- Require C++14
- Support satellite diagonals (from e.g. MOL with PBC)

v0.2.5
======
- Enhanced conda recipe

v0.2.4
======
- More robust setup.py

v0.2.2
======
- More robust setup.py

v0.2.1
======
- More robust setup.py

v0.2.0
======
- solve may now return non-zero exit (in C++, raises error in Python)
- check for NaN in solve
- check for zero diagonal elements in U

v0.1.1
======
- LU bindings in Python

v0.1
====
- Initial release with a minimal Python interface 
