#!/usr/bin/env python
# http://homepages.e3.net.nz/~djm/cppgrammar.html#declaration-seq
import sys
from moc_lexer import Lexer
from ply import lex
from define import *

class Parser(Lexer):
  def __init__(self):
    super(Parser, self).__init__()

  def HasNext(self):
    return self.index_ < len(self.tokens_)

  def Test(self, token):
    if self.index_ >= len(self.tokens_):
      return False
    if self.tokens_[self.index_].type != token:
      return False
    self.index_ += 1
    return True

  def Next(self):
    if self.index_ >= len(self.tokens_):
      return None
    token = self.tokens_[self.index_]
    self.index_ += 1
    return token

  def Prev(self):
    self.index_ -= 1

  def Lookup(self, k):
    return self.tokens_[self.index_ - 1 + k]

  def Until(self, target):
    brace_count = 0
    brack_count = 0
    paren_count = 0

    if self.index_ != 0:
      t = self.tokens_[self.index_ - 1].type
      if t == '{': brace_count += 1
      elif t == '[': brack_count += 1
      elif t == '(': paren_count += 1

    while self.index_ < len(self.tokens_):
      t = self.tokens_[self.index_].type
      self.index_ += 1
      
      if t == '{': brace_count += 1
      elif t == '}': brace_count -= 1
      elif t == '[': brack_count += 1
      elif t == ']': brack_count -= 1
      elif t == '(': paren_count += 1
      elif t == ')': paren_count -= 1
      
      if t == target and \
          brace_count <= 0 and brack_count <= 0 and paren_count <= 0:
        return True
    return False

  def ParseScope(self):
    # TODO(penghuang): Verify scope
    if self.Test('SCOPE'):
      scope = '::'
    else:
      scope = ''
    
    while True:
      token = self.Next()
      if token.type != 'SYMBOL':
        return None
      scope += token.value

      token = self.Next()
      if token.type == '::':
        scope += '::'
        continue
      self.Prev()
      return scope

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
    f = self.Test('ENUM') or \
        self.Test('STRUCT') or \
        self.Test('CLASS') or \
        self.Test('UNION')

    if self.Test('INT') or self.Test('LONG') or self.Test('SHORT') or \
        self.Test('CHAR') or self.Test('FLOAT') or self.Test('DOUBLE'):
      value = self.Lookup(0).value
      type.append(value)
      # Only support long long. Will not support long int, long short and etc
      if value == 'long' and self.Test('LONG'):
        type.append('long')
    elif self.Test('SYMBOL'):
      type.append(self.Lookup(0).value)
    elif self.Test('VOID'):
      is_void = True
      type.append('void')
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
    return TypeDef(' '.join(type))

  def ParseSlot(self):
    if not self.Test('R_SLOT'):
      return None

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
      
      parent_name = self.ParseScope()
      if not parent_name:
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

  def Parse(self, namespace=""):
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

    for c in classes:
      print c

  def ParseFile(self, filename):
    data = open(filename).read()
    self.SetData(filename, data)
    self.tokens_ = []
    self.index_ = 0
    while True:
      t = self.lexobj.token()
      if t is None:
        break
      self.tokens_.append(t)
    self.Parse()


def Main(args):
  parser = Parser()
  parser.ParseFile(args[0])

if __name__ == '__main__':
  Main(sys.argv[1:])
