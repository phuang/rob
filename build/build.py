
__all__ = [
  'CreateNinjaWriter',
  'Executable',
  'Library',
  'Target',
]

import os
import os.path as path
import glob
import ninja_syntax


cflags = '-g -O0 -pthread'
ldflags = '-pthread'
topdir = '.'


def CreateNinjaWriter(p):
  try:
    os.makedirs(path.dirname(p))
  except:
    pass
  return ninja_syntax.Writer(file(p, 'w'))


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
    return CreateNinjaWriter(self.ninja_)

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

