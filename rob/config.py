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
  
  sources = [
    'rob/condition.cc',
    'rob/meta_type.cc',
    'rob/meta_object.cc',
    'rob/mutex.cc',
    'rob/object.cc',
    'rob/read_write_lock.cc',
    'rob/rob.cc',
    'rob/thread.cc',
    'rob/variant.cc'
  ]
  moc_headers = [
    'rob/object.h',
  ]
  includes = ['.']
  lib = Library('librob', sources, includes, moc_headers)
  lib.generate()
  targets.append(lib)
  
  sources = [
    'rob/object_test.cc',
    'rob/rob_unittest.cc',
  ]
  includes = ['.', 'gtest/include']
  deps = ['libgtest', 'librob']
  test = Executable('rob_unittest', sources, includes, deps)
  test.generate()
  targets.append(test)
  
  return targets
