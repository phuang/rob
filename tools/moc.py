#!/usr/bin/env python
import os.path as path
import sys

from define import *
from generator import Generator
from option import ParseOptions
from parser import Parser

class Moc(Parser):
  def __init__(self):
    Parser.__init__(self)

  def ParseScope(self):
    # TODO(penghuang): Verify scope
    s = []
    if self.Test('SCOPE'):
      s.append('')

    while True:
      if not self.Test('SYMBOL'):
        raise Exception('Parse scope failed')
      s.append(self.Lookup(0).value)
      if self.Test('SCOPE'):
        continue
      return "::".join(s)

  def ParseType(self):
    has_signed_or_unsigned = False
    is_void = False
    is_const = False
    is_pointer = False
    is_ref = False
    type = []

    # check const, singed and unsigned
    while True:
      if self.Test('CONST'):
        if is_const:
          raise Exception('Duplicate const.')
        is_const = True
        type.append('const')
        continue
      if self.Test('SIGNED'):
        if has_signed_or_unsigned:
          raise Exception('Duplicate signed or unsigned.')
        has_signed_or_unsigned = True
      if self.Test('UNSIGNED'):
        if has_signed_or_unsigned:
          raise Exception('Duplicate signed or unsigned.')
        has_signed_or_unsigned = True
        type.append('unsigned')
      break

    # Skip enum, struct, class and union
    f = self.Test('ENUM') or self.Test('STRUCT') or \
        self.Test('CLASS') or self.Test('UNION')

    if self.Test('INT') or self.Test('LONG') or self.Test('SHORT') or \
        self.Test('CHAR') or self.Test('FLOAT') or self.Test('DOUBLE'):
      value = self.Lookup(0).value
      type.append(value)
      # Only support long long. Will not support long int, long short and etc
      if value == 'long' and self.Test('LONG'):
        type.append('long')
    elif self.Test('VOID'):
      is_void = True
      type.append('void')
    elif self.Test('SYMBOL'):
      self.Prev()
      type.append(self.ParseScope())
    else:
      raise Exception('Parse type error')

    if self.Test('&'):
      if is_void:
        raise Exception('Parse type error void &')
      is_ref = True
      type.append('&')
    elif self.Test('*'):
      is_pointer = True
      type.append('*')
      if self.Test('CONST'):
        type.append('const')
    return ' '.join(type)

  def ParseFunction(self):
    is_virtual = False
    is_static = False
    while True:
      if self.Test('INLINE'):
         continue
      if self.Test('STATIC'):
        is_static = True
        continue
      if self.Test('VIRTUAL'):
        is_virtual = True
        continue
      break

    if self.Lookup(0).type == 'TEMPLATE':
      raise Exception('Do not support template slot')

    slot_type = self.ParseType()
    if not self.Test('SYMBOL'):
      raise Exception('Parse slot failed')

    slot_name = self.Lookup(0).value
    if not self.Test('('):
      raise Exception('Parse slot failed: expect \'(\'')

    params = []
    while True:
      if self.Test(')'):
        break
      param_type = self.ParseType()
      if self.Test('SYMBOL'):
        param_name = self.Lookup(0).value
      params.append((param_type, param_name))

      if self.Test(')'):
        break
      if not self.Test(','):
        raise Exception('Parse param failed')

    self.Test('CONST')

    if self.Test('='):
      if self.Lookup(1).value != '0':
        raise Exception('Parse slot failed: expect \'0\'')
      if not is_virtual:
        raise Exception('initializer specified for non-virtual')

    if self.Test('{'):
      if not self.Until('}'):
        raise Exception('Parse function failed: EOF')
    elif self.Test(';'):
      pass
    else:
      raise Exception('Parse slot failed: expect \';\'')
    return FunctionDef(slot_name, is_static, is_virtual, slot_type, params)

  def ParseSlot(self):
    if not self.Test('R_SLOT'):
      return None
    return self.ParseFunction()

  def ParseSignal(self):
    if not self.Test('R_SIGNAL'):
      return None
    return self.ParseFunction()

  def ParseProperty(self):
    if not self.Test('R_PROPERTY'):
      return None
    if not self.Test('('):
      raise Exception('Parse property failed: except `(\'')

    prop_type = self.ParseType()
    if not self.Test('SYMBOL'):
      raise Exception('Parse property failed: expect property name.')
    prop_name = self.Lookup(0).value

    if not self.Test('SYMBOL', 'READ'):
      raise Exception('Parse property failed: expect READ')

    if not self.Test('SYMBOL'):
      raise Exception('Parse property failed: expect read function.')
    prop_read = self.Lookup(0).value

    prop_write = None
    if self.Test('SYMBOL', 'WRITE'):
      if not self.Test('SYMBOL'):
        raise Exception('Parse property failed: expect write function.')
      prop_write = self.Lookup(0).value
    if not self.Test(')'):
      raise Exception('Parse property failed: except `)\'')
    return PropertyDef(prop_name, prop_type, prop_read, prop_write)

  def ParseClass(self):
    class_name = None
    parent_name = None
    paraent_access = 'PRIVATE'
    access = 'PRIVATE'
    r_object = False

    if self.Test('CLASS'):
      access = 'PRIVATE'
    elif self.Test('STRUCT'):
      access = 'PUBLIC'
    else:
      return False, None

    # ignore ROB_EXPORT macro
    self.Test('SYMBOL', 'ROB_EXPORT')

    token = self.Next()
    if token.type != 'SYMBOL':
      raise Exception('Parse class error: expect class name')

    class_name = token.value

    if self.Test(';'): # Forward define class Foo;
      return True, None

    parent_access = 'PRIVATE'
    if self.Test(':'): #
      if self.Test('PUBLIC') or self.Test('PRIVATE') or self.Test('PROTECTED'):
        parent_access = self.Lookup(0).type

      try:
        parent_name = self.ParseScope()
      except:
        raise Exception("Parse parent class name of class %s error!", class_name)

    if not self.Test('{'):
      raise Exception('Parse class error: expect `{\'')

    if not self.Test('R_OBJECT'):
      if self.Until('}'):
        if self.Test(';'):
          return True, None
        else:
          raise Exception('Parse class %s failed: except `;\'' % class_name)
      else:
        raise Exception('Parse class %s failed: EOF', class_name)

    class_def = ClassDef(class_name, parent_name, parent_access)

    while self.HasNext():
      # End of class
      if self.Test('}'):
        if self.Test(';'):
          return True, class_def
        raise Exception('Parse class error: expect `;\'')

      # Parse public, private and protected
      if self.Test('PUBLIC') or self.Test('PRIVATE') or self.Test('PROTECTED'):
        access = self.Lookup(0).type
        if not self.Test(':'):
          raise Exception('Parse class error: expect `:\'')
        continue

      # Parse slot
      slot_def = self.ParseSlot()
      if slot_def:
        if access != 'PUBLIC':
          raise Exception('Slot must be public')
        class_def.slots.append(slot_def)
        continue

      # Parse ssignal
      signal_def = self.ParseSignal()
      if signal_def:
        if access != 'PUBLIC':
          raise Exception('Signal must be public')
        class_def.signals.append(signal_def)
        continue

      prop_def = self.ParseProperty()
      if prop_def:
        class_def.properties.append(prop_def)

      self.Until(';')

    raise Exception('Parse class \'%s\' error EOF' % class_name)

  def ParseNamespace(self):
    name = ""
    if not self.Test('NAMESPACE'):
      return None

    token = self.Next()
    if token.type == 'SYMBOL':
      name = token.value
      if self.Test('='): # namespace Foo = Bar::Baz;
          self.Until(';')
          return None
    if not self.Test('{'):
      return None
    begin = self.index_;
    if not self.Until('}'):
      return None
    return NamespaceDef(name, begin, self.index_)

  def Parse(self):
    namespaces = []
    classes = []
    while self.HasNext():
      namespace = self.ParseNamespace()
      if namespace:
        namespaces.append(namespace)
        self.index_ = namespace.begin
        continue
      if self.Test(';'): continue
      if self.Test('}'): continue
      if self.Test('INCLUDE'): continue
      if self.Test('DEFINE'): continue
      if self.Test('IF'): continue
      if self.Test('IFDEF'): continue
      if self.Test('IFNDEF'): continue
      if self.Test('ELSE'): continue
      if self.Test('ELIF'): continue
      if self.Test('ENDIF'): continue

      if self.Test('USING'):
        self.Until(';')
        continue

      class_index = self.index_
      is_class, class_def = self.ParseClass()
      if class_def:
        nss = []
        for ns in namespaces:
          if class_index >= ns.begin and class_index < ns.end:
            nss.append(ns.name)
        class_def.namespace = "::".join(nss)
        classes.append(class_def)
      if is_class:
        continue

      # Move to ; or }
      cur = self.index_
      self.Until(';')
      p1 = self.index_
      self.index_ = cur
      self.Until('}')
      p2 = self.index_
      self.index_ = p1 if p1 <= p2 else p2

    generator = Generator()
    print generator.Generate(self.filename_, classes)

  def ParseFile(self, filename):
    data = open(filename).read()
    self.SetData(filename, data)
    self.filename_ = path.basename(filename)
    self.tokens_ = []
    self.index_ = 0
    while True:
      t = self.lexobj.token()
      if t is None:
        break
      self.tokens_.append(t)
    self.Parse()


def Main(args):
  filenames = ParseOptions(args)

  moc = Moc()
  for f in filenames:
    moc.ParseFile(f)


if __name__ == '__main__':
  Main(sys.argv[1:])
