#!/usr/bin/env python

import imp
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
  targets = GenerateSubninjas()

  for target in targets:
    out.subninja(target.get_ninja())

  out.newline()
  all = [ target.get_name() for target in targets]
  out.build('all', 'phony', all)

def GenerateSubninjas():
  targets = []
  for root, dirs, files in os.walk('.'):
    if 'config.py' not in files:
      continue
    configfile = path.join(root, 'config.py')
    config = imp.load_source('config', configfile)
    targets += config.get_targets()
  return targets

def Main(args):
  GenerateBuild()
  GenerateSubninjas()

if __name__ == '__main__':
  Main(sys.argv)
