#!/usr/bin/env python
# Copyright (c) 2012 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

""" Lexer for C++ Header file """

#
# IDL Lexer
#
# The lexer is uses the PLY lex library to build a tokenizer which understands
# WebIDL tokens.
#
# WebIDL, and WebIDL regular expressions can be found at:
#   http://dev.w3.org/2006/webapi/WebIDL/
# PLY can be found at:
#   http://www.dabeaz.com/ply/

import os.path
import re
import sys

#
# Try to load the ply module, if not, then assume it is in the third_party
# directory, relative to ppapi
#
try:
  from ply import lex
except:
  module_path, module_name = os.path.split(__file__)
  third_party = os.path.join(module_path, '..', '..', 'third_party')
  sys.path.append(third_party)
  from ply import lex


#
# IDL Lexer
#
class Lexer(object):
  # 'tokens' is a value required by lex which specifies the complete list
  # of valid token types.
  tokens = [
    # Symbol and keywords types
      'CLASS',
      'COMMENT',
      'ENUM',
      'SYMBOL',
      'INLINE',
      'STRUCT',
      'TYPEDEF',
      'STATIC',
      'PUBLIC',
      'PRIVATE',
      'PROTECTED',
      'NAMESPACE',
      'INCLUDE',
      'VIRTUAL',
      'RETURN',
      'CONST',

    # Data types
      'FLOAT',
      'OCT',
      'INT',
      'HEX',
      'STRING',

    # Operators
      'LSHIFT',
      'RSHIFT'
  ]

  # 'keywords' is a map of string to token type.  All SYMBOL tokens are
  # matched against keywords, to determine if the token is actually a keyword.
  keywords = {
    'class' : 'CLASS',
    'describe' : 'DESCRIBE',
    'enum'  : 'ENUM',
    'namespace' : 'NAMESPACE',
    'static' : 'STATIC',
    'struct' : 'STRUCT',
    'typedef' : 'TYPEDEF',
    'public' : 'PUBLIC',
    'protected' : 'PROTECTED',
    'private' : 'PRIVATE',
    'inline' : 'INLINE',
    'virtual' : 'VIRTUAL',
    'explicit' : 'EXPLICIT',
    'return' : 'RETURN',
    'const' : 'CONST',
  }

  # 'literals' is a value expected by lex which specifies a list of valid
  # literal tokens, meaning the token type and token value are identical.
  literals = '"*.(){}[],;:=+-/~|&^?'

  # Token definitions
  #
  # Lex assumes any value or function in the form of 't_<TYPE>' represents a
  # regular expression where a match will emit a token of type <TYPE>.  In the
  # case of a function, the function is called when a match is made. These
  # definitions come from WebIDL.

  # 't_ignore' is a special match of items to ignore
  t_ignore = ' \t'

  # Constant values
  t_FLOAT = r'-?(\d+\.\d*|\d*\.\d+)([Ee][+-]?\d+)?|-?\d+[Ee][+-]?\d+'
  t_INT = r'-?[0-9]+[uU]?'
  t_OCT = r'-?0[0-7]+'
  t_HEX = r'-?0[Xx][0-9A-Fa-f]+'
  t_LSHIFT = r'<<'
  t_RSHIFT = r'>>'

  # A line ending '\n', we use this to increment the line number
  def t_LINE_END(self, t):
    r'\n+'
    self.AddLines(len(t.value))

  # We do not process escapes in the IDL strings.  Strings are exclusively
  # used for attributes, and not used as typical 'C' constants.
  def t_STRING(self, t):
    r'"[^"]*"'
    t.value = t.value[1:-1]
    self.AddLines(t.value.count('\n'))
    return t

  # A C or C++ style comment:  /* xxx */ or //
  def t_COMMENT(self, t):
    r'(/\*(.|\n)*?\*/)|(//.*(\n[ \t]*//.*)*)'
    self.AddLines(t.value.count('\n'))
    return t

  # Return a "preprocessor" inline block
  def t_INCLUDE(self, t):
    r'\#include .*\n'
    self.AddLines(t.value.count('\n'))
    return t

  # A symbol or keyword.
  def t_KEYWORD_SYMBOL(self, t):
    r'_?[A-Za-z][A-Za-z_0-9]*'

    # All non-keywords are assumed to be symbols
    t.type = self.keywords.get(t.value, 'SYMBOL')
    return t

  def t_ANY_error(self, t):
    msg = "Unrecognized input"
    line = self.lexobj.lineno

    # If that line has not been accounted for, then we must have hit
    # EoF, so compute the beginning of the line that caused the problem.
    if line >= len(self.index):
      # Find the offset in the line of the first word causing the issue
      word = t.value.split()[0]
      offs = self.lines[line - 1].find(word)
      # Add the computed line's starting position
      self.index.append(self.lexobj.lexpos - offs)
      msg = "Unexpected EoF reached after"

    pos = self.lexobj.lexpos - self.index[line]
    file = self.lexobj.filename
    out = self.ErrorMessage(file, line, pos, msg)
    sys.stderr.write(out + '\n')
    self.lex_errors += 1


  def AddLines(self, count):
    # Set the lexer position for the beginning of the next line.  In the case
    # of multiple lines, tokens can not exist on any of the lines except the
    # last one, so the recorded value for previous lines are unused.  We still
    # fill the array however, to make sure the line count is correct.
    self.lexobj.lineno += count
    for i in range(count):
      self.index.append(self.lexobj.lexpos)

  def FileLineMsg(self, file, line, msg):
    if file:  return "%s(%d) : %s" % (file, line + 1, msg)
    return "<BuiltIn> : %s" % msg

  def SourceLine(self, file, line, pos):
    caret = '\t^'.expandtabs(pos)
    # We decrement the line number since the array is 0 based while the
    # line numbers are 1 based.
    return "%s\n%s" % (self.lines[line - 1], caret)

  def ErrorMessage(self, file, line, pos, msg):
    return "\n%s\n%s" % (
        self.FileLineMsg(file, line, msg),
        self.SourceLine(file, line, pos))

  def SetData(self, filename, data):
    # Start with line 1, not zero
    self.lexobj.lineno = 1
    self.lexobj.filename = filename
    self.lines = data.split('\n')
    self.index = [0]
    self.lexobj.input(data)
    self.lex_errors = 0

  def __init__(self):
    self.lexobj = lex.lex(object=self, lextab=None, optimize=0)



#
# FilesToTokens
#
# From a set of source file names, generate a list of tokens.
#
def FilesToTokens(filenames, verbose=False):
  lexer = Lexer()
  outlist = []
  for filename in filenames:
    data = open(filename).read()
    lexer.SetData(filename, data)
    if verbose: sys.stdout.write('  Loaded %s...\n' % filename)
    while 1:
      t = lexer.lexobj.token()
      if t is None: break
      outlist.append(t)
  return outlist


def TokensFromText(text):
  lexer = Lexer()
  lexer.SetData('unknown', text)
  outlist = []
  while 1:
    t = lexer.lexobj.token()
    if t is None: break
    outlist.append(t.value)
  return outlist

#
# TextToTokens
#
# From a block of text, generate a list of tokens
#
def TextToTokens(source):
  lexer = Lexer()
  outlist = []
  lexer.SetData('AUTO', source)
  while 1:
    t = lexer.lexobj.token()
    if t is None: break
    outlist.append(t.value)
  return outlist


def Main(args):
  filenames = ['counter.h']

  try:
    tokens = FilesToTokens(filenames, True)
    # symbols = [tok.value for tok in tokens if tok.type == 'SYMBOL' ]
    # print symbols
    for tok in tokens:
      print tok
  
  except lex.LexError as le:
    sys.stderr.write('%s\n' % str(le))
  return -1


if __name__ == '__main__':
  sys.exit(Main(sys.argv[1:]))
