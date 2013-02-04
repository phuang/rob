from build import *
import glob
import os.path as path

srcdir = 'rob'

def get_targets():
  targets = []

  sources =  filter(lambda f: f[-8:] != '_test.cc', glob.glob(path.join(srcdir, '*.cc')))
  moc_headers = [
    'rob/object.h',
  ]
  includes = ['.']
  lib = Library('librob', sources, includes, moc_headers)
  lib.generate()
  targets.append(lib)
  
  sources = glob.glob(path.join(srcdir, '*_test.cc'))
  deps = ['libgtest', 'librob']
  includes = ['.', 'gtest/include']
  test = Executable('rob_unittest', sources, includes, deps)
  test.generate()
  targets.append(test)
  
  return targets

if __name__ == '__main__':
  pass
