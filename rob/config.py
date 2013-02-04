from build import *
import glob
import os.path as path

srcdir = 'rob'

def get_targets():
  targets = []

  # librob
  sources =  filter(lambda f: f[-8:] != '_test.cc', glob.glob(path.join(srcdir, '*.cc')))
  moc_headers = [
    'rob/object.h',
  ]
  includes = ['.']
  targets += [Library('librob', sources, includes, moc_headers)]

  # unit tests
  sources = glob.glob(path.join(srcdir, '*_test.cc'))
  deps = ['libgtest', 'librob']
  includes = ['.', 'gtest/include']
  targets += [Executable('rob_unittest', sources, includes, deps)]
  
  return targets

if __name__ == '__main__':
  pass
