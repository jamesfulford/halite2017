#!/bin/bash
#install.sh

python3.6 -m pip install --system --target .


# TODO:
#
# precompile code (numba.jit?)
# memoize functions (distance between planets)
#   refactor lots of distance measurements as distance between nearest planet and planet
#   (to leverage memoization more)
# refactor handle_* to just aquire targets
# handle_mining at the forces level to ensure we don't overallocate
# diagnose why defending until masses built up does not work
# ships no longer seek mining as actively; act very differently after all planets filled
#

