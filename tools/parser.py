#!/usr/bin/env python
# http://homepages.e3.net.nz/~djm/cppgrammar.html#declaration-seq
from moc_lexer import Lexer

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

