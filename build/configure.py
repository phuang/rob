#!/usr/bin/env python

import os
import os.path as path
import sys
import glob
import ninja_syntax

_path = os.path.dirname(__file__)
if _path not in sys.path:
  sys.path.append(_path)


cflags = '-g -O0 -pthread'
ldflags = '-pthread'
topdir = '..'

def CreateWriter(p):
  try:
    os.makedirs(path.dirname(p))
  except:
    pass
  return ninja_syntax.Writer(file(p, 'w'))

def GenerateBuild():
  out = CreateWriter('out/build.ninja')
  
  out.variable('cc', 'gcc')
  out.variable('cxx', 'g++')
  out.variable('ld', 'flock linker.lock $cxx')
  out.variable('ar', 'ar')
  
  out.newline()
  
  command = '%s -MMD -MF $out.d $defines $includes $cflags $cflags_c $cflags_pch_c -c $in -o $out'
  out.rule('cc', command % '$cc', 'CC $out', '$out.d')
  out.rule('cxx', command % '$cxx', 'CXX $out', '$out.d')
  out.rule('alink', 'rm -f $out && $ar rcs $out $in', 'AR $out')
  out.rule('alink_thin', 'rm -f $out && $ar rcsT $out $in', 'AR $out')
  out.rule('link', '$ld $ldflags -o $out -Wl,--start-group $in $solibs -Wl,--end-group $libs', 'LINK $out')  
  
  out.newline()
  out.subninja('obj/libgtest/build.ninja')
  out.subninja('obj/librob/build.ninja')
  out.subninja('obj/rob_unittest/build.ninja')

  out.newline()
  all = [
    'obj/libgtest/libgtest.a',
    'obj/librob/librob.a',
    'obj/rob_unittest/rob_unittest'
 ]
  out.build('all', 'phony', all)

class Target(object):
  def __init__(self, name):
    object.__init__(self)
    self.obj_path_ = path.join('obj', name)
    self.ninja_ = path.join('out', self.obj_path_, 'build.ninja')
    self.writer_ = CreateWriter(self.ninja_)

  def get_ninja(self):
    return self.ninja_

  def get_obj_path(self, name):
    return path.join(self.obj_path_, name)

class Library(Target):
  def __init__(self, name, sources, includes):
    Target.__init__(self, name)
    
    includes = ['-I%s' % path.join(topdir, i) for i in includes]
    self.writer_.variable('includes', ' '.join(includes))
    self.writer_.variable('cflags', cflags)

    self.writer_.newline()

    objs = []
    for src in sources:
      fname, fext = src.rsplit('.', 1)
      obj = path.join('obj', name, fname + '.o')
      src = path.join(topdir, src)
      self.writer_.build(obj, 'cxx', src)
      objs.append(obj)
 
    output = self.get_obj_path(name) + '.a'
    self.writer_.build(output, 'alink_thin', objs)
    self.writer_.build(name, 'phony', output)

class Executable(Target):
  def __init__(self, name, sources, includes, deps):
    Target.__init__(self, name)
    
    includes = ['-I%s' % path.join(topdir, i) for i in includes]
    self.writer_.variable('includes', ' '.join(includes))
    self.writer_.variable('cflags', cflags)
    self.writer_.variable('ldflags', ldflags)

    self.writer_.newline()

    objs = []
    for src in sources:
      fname, fext = src.rsplit('.', 1)
      obj = path.join('obj', name, fname + '.o')
      src = path.join(topdir, src)
      self.writer_.build(obj, 'cxx', src)
      objs.append(obj)
 
    deps = [path.join('obj', d, d + '.a') for d in deps]
  
    output = self.get_obj_path(name)
    self.writer_.build(output, 'link', deps + objs)
    self.writer_.build(name, 'phony', output)

def GenerateSubninjas():
  sources = [
    'gtest/src/gtest-all.cc',
    'gtest/src/gtest_main.cc',
  ]
  includes = [ 'gtest', 'gtest/include']
  Library('libgtest', sources, includes)
  
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
  includes = ['.']
  Library('librob', sources, includes)
  
  sources = [
    'rob/rob_unittest.cc',
  ]
  includes = ['.', 'gtest/include']
  deps = ['libgtest', 'librob']
  Executable('rob_unittest', sources, includes, deps)



def Main(args):
  GenerateBuild()
  GenerateSubninjas()

if __name__ == '__main__':
  Main(sys.argv)
