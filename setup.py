#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import logging
import os
import re
import shutil
import subprocess
import sys
import warnings

from setuptools import setup, Extension
try:
    import cython
except ImportError:
    _HAVE_CYTHON = False
else:
    _HAVE_CYTHON = True
    assert cython  # silence pep8


pkg_name = 'block_diag_ilu'
url = 'https://github.com/chemreac/' + pkg_name
license = 'BSD'


def _path_under_setup(*args):
    return os.path.join(*args)

release_py_path = _path_under_setup(pkg_name, '_release.py')
config_py_path = _path_under_setup(pkg_name, '_config.py')

_version_env_var = '%s_RELEASE_VERSION' % pkg_name.upper()
_RELEASE_VERSION = os.environ.get(_version_env_var, '')


if len(_RELEASE_VERSION) > 1:
    if _RELEASE_VERSION[0] != 'v':
        raise ValueError("$%s does not start with 'v'" % _version_env_var)
    TAGGED_RELEASE = True
    __version__ = _RELEASE_VERSION[1:]
else:  # set `__version__` from _release.py:
    TAGGED_RELEASE = False
    exec(open(release_py_path).read())
    if __version__.endswith('git'):
        try:
            _git_version = subprocess.check_output(
                ['git', 'describe', '--dirty']).rstrip().decode('utf-8').replace('-dirty', '+dirty')
        except subprocess.CalledProcessError:
            warnings.warn("A git-archive is being installed - version information incomplete.")
        else:
            if 'develop' not in sys.argv:
                warnings.warn("Using git to derive version: dev-branches may compete.")
                _ver_tmplt = r'\1.post\2' if os.environ.get('CONDA_BUILD', '0') == '1' else r'\1.post\2+\3'
                __version__ = re.sub(r'v([0-9.]+)-(\d+)-(\S+)', _ver_tmplt, _git_version)  # .dev < '' < .post


package_include = os.path.join(pkg_name, 'include')
basename = '_%s' % pkg_name
_src = {ext: _path_under_setup(pkg_name, "%s.%s" % (basename, ext)) for ext in "cpp pyx".split()}
if os.path.exists(_src["pyx"]):
    # Possible that a new release of Python needs a re-rendered Cython source,
    # or that we want to include possible bug-fix to Cython.
    USE_CYTHON = True
    if os.path.exists(_src["cpp"]):
        os.unlink(_src["cpp"])  # ensure c++ source is re-generated.
else:
    USE_CYTHON = False

ext_modules = []

if len(sys.argv) > 1 and '--help' not in sys.argv[1:] and sys.argv[1] not in (
        '--help-commands', 'egg_info', 'clean', '--version'):
    import numpy as np
    env = None  # silence pyflakes, 'env' is actually set on the next line
    exec(open(config_py_path).read())
    for k, v in list(env.items()):
        env[k] = os.environ.get('%s_%s' % (pkg_name.upper(), k), v)
    logger = logging.getLogger(__name__)
    logger.info("Config for %s: %s" % (pkg_name, str(env)))
    ext_modules = [Extension('%s._%s' % (pkg_name, pkg_name), [_src["pyx" if USE_CYTHON else "cpp"]])]
    if USE_CYTHON:
        from Cython.Build import cythonize
        ext_modules = cythonize(ext_modules, include_path=[package_include])
    else:
        if not os.path.exists(_src["cpp"]):
            raise ValueError("Neither pyx nor cpp file found")

    macros = [('BLOCK_DIAG_ILU_PY', None)]
    if env.get('BLOCK_DIAG_ILU_WITH_GETRF') == '1':
        macros.append(('BLOCK_DIAG_ILU_WITH_GETRF', None))
    if env.get('BLOCK_DIAG_ILU_WITH_OPENMP') == '1':
        macros.append(('BLOCK_DIAG_ILU_WITH_OPENMP', None))
    ext_modules[0].language = 'c++'
    ext_modules[0].extra_compile_args = ['-std=c++11']
    ext_modules[0].include_dirs = [
        np.get_include(),
        package_include,
        os.path.join('external', 'anyode', 'include')
    ]
    ext_modules[0].define_macros += macros
    ext_modules[0].libraries += env['LAPACK'].split(',')

classifiers = [
    "Development Status :: 4 - Beta",
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Topic :: Scientific/Engineering',
    'Topic :: Scientific/Engineering :: Mathematics',
]

tests = [
    '%s.tests' % pkg_name,
]

with io.open(_path_under_setup(pkg_name, '__init__.py'), 'rt', encoding='utf-8') as f:
    short_description = f.read().split('"""')[1].split('\n')[1]
if not 10 < len(short_description) < 255:
    warnings.warn("Short description from __init__.py proably not read correctly.")
# long_description = io.open(_path_under_setup('README.rst'),
#                            encoding='utf-8').read()
# if not len(long_description) > 100:
#     warnings.warn("Long description from README.rst probably not read correctly.")
_author, _author_email = open(_path_under_setup('AUTHORS'), 'rt').readline().split('<')

setup_kwargs = dict(
    name=pkg_name,
    version=__version__,
    description=short_description,
    # long_description=long_description,
    classifiers=classifiers,
    author=_author.strip(),
    author_email=_author_email.split('>')[0].strip(),
    url=url,
    license=license,
    packages=[pkg_name] + tests,
    include_package_data=True,
    setup_requires=['numpy', 'cython'],
    install_requires=['numpy'],
    ext_modules=ext_modules,
)

if __name__ == '__main__':
    try:
        if TAGGED_RELEASE:
            # Same commit should generate different sdist files
            # depending on tagged version (see RELEASE_VERSION)
            # this will ensure source distributions contain the correct version
            shutil.move(release_py_path, release_py_path+'__temp__')
            open(release_py_path, 'wt').write(
                "__version__ = '{}'\n".format(__version__))
        setup(**setup_kwargs)
    finally:
        if TAGGED_RELEASE:
            shutil.move(release_py_path+'__temp__', release_py_path)
