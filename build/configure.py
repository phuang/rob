#!/usr/bin/env python

import os
import os.path as path
import sys
import glob
import ninja_syntax

from build import *

_path = os.path.dirname(__file__)
if _path not in sys.path:
  sys.path.append(_path)

def GenerateBuild():
  out = CreateNinjaWriter('build.ninja')
  
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
