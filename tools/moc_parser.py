#!/usr/bin/env python
# http://homepages.e3.net.nz/~djm/cppgrammar.html#declaration-seq

from moc_lexer import Lexer

from ply import lex
from ply import yacc

class Parser(Lexer):
  def p_translation_unit_1(self, p):
    '''translation_unit : '''
    pass
  
  def p_translation_unit_2(self, p):
    '''translation_unit : declaration_seq'''
    pass

  def p_declaration_seq_1(self, p):
    '''declaration_seq : declaration'''
    pass

  def p_declaration_seq_2(self, p):
    '''declaration_seq : declaration_seq declaration'''
    pass

  def p_declaration_1(self, p):
    '''declaration : block_declaration'''
    pass
  
  def p_declaration_2(self, p):
    '''declaration : function_declaration'''
    pass
  
  def p_declaration_3(self, p):
    '''declaration : template_declaration'''
    pass

  def p_declaration_4(self, p):
    '''declaration : explicit_instatiation'''
    pass
  
  def p_declaration_4(self, p):
    '''declaration : explicit_specialization'''
    pass
  
  def p_declaration_5(self, p):
    '''declaration : linkage_specification'''
    pass

  def p_declaration_6(self, p):
    '''declaration : namespace_definition'''
    pass

  def p_declaration_5(self, p):
    '''declaration : namespace_definition'''
    pass


  def __init__(self):
    super(Parser, self).__init__()

