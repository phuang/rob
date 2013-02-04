#!/usr/bin/env python

__all__ = [
  'Target',
  'Library',
  'Executable'
]

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
topdir = '.'

def CreateWriter(p):
  try:
    os.makedirs(path.dirname(p))
  except:
    pass
  return ninja_syntax.Writer(file(p, 'w'))

def GenerateBuild():
  out = CreateWriter('build.ninja')
  
  out.variable('cc', 'gcc')
  out.variable('cxx', 'g++')
  out.variable('ld', 'flock linker.lock $cxx')
  out.variable('ar', 'ar')
  out.variable('moc', 'tools/moc.py')
  
  out.newline()
  
  command = '%s -MMD -MF $out.d $defines $includes $cflags $cflags_c $cflags_pch_c -c $in -o $out'
  out.rule('cc', command % '$cc', 'CC $out', '$out.d')
  out.rule('cxx', command % '$cxx', 'CXX $out', '$out.d')
  out.rule('alink', 'rm -f $out && $ar rcs $out $in', 'AR $out')
  out.rule('alink_thin', 'rm -f $out && $ar rcsT $out $in', 'AR $out')
  out.rule('link', '$ld $ldflags -o $out -Wl,--start-group $in $solibs -Wl,--end-group $libs', 'LINK $out')  
  out.rule('moc', '$moc $in $out $out.d', 'MOC $out', '$out.d')

  out.newline()
  out.subninja('out/obj/libgtest/build.ninja')
  out.subninja('out/obj/librob/build.ninja')
  out.subninja('out/obj/rob_unittest/build.ninja')

  out.newline()
  all = [
    'out/obj/libgtest/libgtest.a',
    'out/obj/librob/librob.a',
    'out/obj/rob_unittest/rob_unittest'
 ]
  out.build('all', 'phony', all)

class Target(object):
  def __init__(self, name):
    object.__init__(self)
    self.name_ = name
    self.obj_path_ = path.join('out', 'obj', name)
    self.ninja_ = path.join(self.obj_path_, 'build.ninja')

  def get_name(self):
    return self.name_

  def get_ninja(self):
    return self.ninja_

  def get_obj_path(self, name):
    return path.join(self.obj_path_, name)

  def get_writer(self):
    return CreateWriter(self.ninja_)

  def generate(self):
    raise NotImplemented()

class Library(Target):
  def __init__(self, name, sources, includes, moc_headers = []):
    Target.__init__(self, name)
    self.sources_ = sources
    self.includes_ = includes
    self.moc_headers_ = moc_headers
  
  def generate(self):
    writer = self.get_writer()

    includes = ['-I%s' % path.join(topdir, i) for i in self.includes_]
    
    writer.variable('includes', ' '.join(includes))
    writer.variable('cflags', cflags)

    writer.newline()

    objs = []
    for src in self.sources_:
      fname, fext = src.rsplit('.', 1)
      obj = self.get_obj_path(fname + '.o')
      src = path.join(topdir, src)
      writer.build(obj, 'cxx', src)
      objs.append(obj)

    for header in self.moc_headers_:
      fname, fext = header.rsplit('.', 1)
      moc_src = self.get_obj_path(fname + '_moc.cc')
      moc_obj = self.get_obj_path(fname + '_moc.o')
      header = path.join(topdir, header)
      writer.build(moc_src, 'moc', header)
      writer.build(moc_obj, 'cxx', moc_src)
      objs.append(moc_obj)
 
    output = self.get_obj_path(self.get_name() + '.a')
    writer.build(output, 'alink_thin', objs)
    writer.build(self.get_name(), 'phony', output)

class Executable(Target):
  def __init__(self, name, sources, includes, deps=[], moc_headers=[]):
    Target.__init__(self, name)
    self.sources_ = sources
    self.includes_ = includes
    self.deps_ = deps
    self.moc_headers_ = moc_headers
    
  def generate(self):
    writer = self.get_writer()

    includes = ['-I%s' % path.join(topdir, i) for i in self.includes_]
    writer.variable('includes', ' '.join(includes))
    writer.variable('cflags', cflags)
    writer.variable('ldflags', ldflags)

    writer.newline()

    objs = []
    for src in self.sources_:
      fname, fext = src.rsplit('.', 1)
      obj = self.get_obj_path(fname + '.o')
      src = path.join(topdir, src)
      writer.build(obj, 'cxx', src)
      objs.append(obj)
    
    for header in self.moc_headers_:
      fname, fext = header.rsplit('.', 1)
      moc_src = self.get_obj_path(fname + '_moc.cc')
      moc_obj = self.get_obj_path(fname + '_moc.o')
      writer.build(moc_src, 'moc', src)
      writer.build(moc_obj, 'cxx', moc_src)
      objs.append(moc_obj)
 
    deps = [path.join('out', 'obj', d, d + '.a') for d in self.deps_]
  
    output = self.get_obj_path(self.get_name())
    writer.build(output, 'link', deps + objs)
    writer.build(self.get_name(), 'phony', output)

def GenerateSubninjas():
  sources = [
    'gtest/src/gtest-all.cc',
    'gtest/src/gtest_main.cc',
  ]
  includes = [ 'gtest', 'gtest/include']
  Library('libgtest', sources, includes).generate()
  
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
  Library('librob', sources, includes, moc_headers).generate()
  
  sources = [
    'rob/object_test.cc',
    'rob/rob_unittest.cc',
  ]
  includes = ['.', 'gtest/include']
  deps = ['libgtest', 'librob']
  Executable('rob_unittest', sources, includes, deps).generate()


def Main(args):
  GenerateBuild()
  GenerateSubninjas()

if __name__ == '__main__':
  Main(sys.argv)
