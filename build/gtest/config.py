from build import *

def get_targets():
  sources = [
    'gtest/src/gtest-all.cc',
    'gtest/src/gtest_main.cc',
  ]
  includes = [ 'gtest', 'gtest/include']
  return [Library('libgtest', sources, includes)]
