#!/usr/bin/env python
# http://homepages.e3.net.nz/~djm/cppgrammar.html#declaration-seq
import sys
from moc_lexer import Lexer

from ply import lex

class TypeDef(object):
  def __init__(self):
    object.__init__(self)

class FunctionDef(object):
  def __init__(self):
    object.__init__(self)

class ClassDef(object):
  def __init__(self, name, parent, parent_access):
    object.__init__(self)
    self.name = name
    self.namespace = None
    self.parent = parent
    self.parentaccess_ = parent_access
    self.slots = []
    self.signals = []
    self.properties = []

  def __str__(self):
    return 'ClassDef[%s]' % self.name

  def __repr__(self):
    return 'NamespaceDef[%s]' % self.name

class NamespaceDef(object):
  def __init__(self, name, begin, end):
    object.__init__(self)
    self.name = name
    self.begin = begin
    self.end = end
  
  def __str__(self):
    return 'NamespaceDef[%s]' % self.name

  def __repr__(self):
    return 'NamespaceDef[%s]' % self.name

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

    type = self.ParseType()

 
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

      is_class, class_def = self.ParseClass()
      if class_def:
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

    print namespaces
    print classes

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
