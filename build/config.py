from build import *

def get_targets():
  targets = []
  sources = [
    'gtest/src/gtest-all.cc',
    'gtest/src/gtest_main.cc',
  ]
  includes = [ 'gtest', 'gtest/include']
  lib = Library('libgtest', sources, includes)
  lib.generate()
  targets.append(lib)
  return targets
