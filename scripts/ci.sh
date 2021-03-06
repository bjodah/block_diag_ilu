#!/bin/bash -xeu
if ! [[ $(python3 setup.py --version) =~ ^[0-9]+.* ]]; then
    exit 1
fi
./scripts/get_external.sh
(
    cd tests
    export ASAN_SYMBOLIZER_PATH=/usr/lib/llvm-10/bin/llvm-symbolizer
    export ASAN_OPTIONS=symbolize=1
    make clean; make CXX=clang++-10 EXTRA_FLAGS="-fsanitize=address"
    make clean; make CXX=g++-10 DEFINES="-D_GLIBCXX_DEBUG -D_GLIBCXX_DEBUG_PEDANTIC -D_FORTIFY_SOURCE=2"
    # make clean; make DEFINES="-DNDEBUG -DBLOCK_DIAG_ILU_WITH_GETRF" LIBS=""
    make clean; make test_block_diag_omp
    BLOCK_DIAG_ILU_NUM_THREADS=2 ./test_block_diag_omp --abortx 1
)

python3 setup.py sdist
VERSION=$(python3 setup.py --version)
PKG_NAME=$1
BRANCH=${2:-$DRONE_TAG}
echo "Branch/tag: $BRANCH"
(cd dist/; python3 -m pip install $PKG_NAME-$VERSION.tar.gz)
(cd /; python3 -m pytest --pyargs $PKG_NAME)
(cd dist/; BLOCK_DIAG_ILU_WITH_OPENMP=1 python3 -m pip install --force-reinstall $PKG_NAME-$VERSION.tar.gz)
(cd /; BLOCK_DIAG_ILU_NUM_THREADS=2 python3 -m pytest --pyargs $PKG_NAME)


(
    cd python_prototype
    PYTHONPATH=$(pwd) python3 -m pytest
    python3 setup.py build_ext -i
    PYTHONPATH=$(pwd) USE_FAST_FAKELU=1 python3 -m pytest
    PYTHONPATH=$(pwd) python3 demo.py
    rm _block_diag_ilu*.so
    BLOCK_DIAG_ILU_WITH_GETRF=1 python3 setup.py build_ext -i
    PYTHONPATH=$(pwd) USE_FAST_FAKELU=1 python3 -m pytest
    PYTHONPATH=$(pwd) python3 demo.py
    rm _block_diag_ilu*.so
    BLOCK_DIAG_ILU_WITH_OPENMP=1 BLOCK_DIAG_ILU_WITH_GETRF=0 python3 setup.py build_ext -i
    PYTHONPATH=$(pwd) USE_FAST_FAKELU=1 python3 -m pytest
    PYTHONPATH=$(pwd) python3 demo.py
    rm _block_diag_ilu*.so
    BLOCK_DIAG_ILU_WITH_OPENMP=1 BLOCK_DIAG_ILU_WITH_GETRF=1 python3 setup.py build_ext -i
    PYTHONPATH=$(pwd) USE_FAST_FAKELU=1 python3 -m pytest
    PYTHONPATH=$(pwd) python3 demo.py

    if [[ "$2" == "master" ]]; then
        ./run_demo.sh
        mkdir -p ../deploy/public_html/branches/"$2"/
        cp run_demo.out demo_out.png  ../deploy/public_html/branches/"$2"/
    fi
)

# Make sure repo is pip installable from git-archive zip
git-archive-all --prefix="" /tmp/archive.zip # git-archive-all includes submodules in external/
(
    cd /
    python3 -m pip install --force-reinstall /tmp/archive.zip
    python3 -c '
from block_diag_ilu import get_include as gi
import os
assert "block_diag_ilu.pxd" in os.listdir(gi())
'
)

(
    cd scripts/
    python3 generate_infographics.py --ndiag 3 --N 15
    python3 generate_infographics.py --savefig periodic -p --ndiag 3 --N 15
    python3 generate_infographics.py --savefig interpolating -i --ndiag 3 --N 15
    mkdir -p ../deploy/public_html/branches/"$2"/
    cp *.png ../deploy/public_html/branches/"$2"/
)

if grep "DO-NOT-MERGE!" -R . --exclude ci.sh; then exit 1; fi
