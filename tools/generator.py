from cStringIO import StringIO

class Generator(object):
  def __init__(self, class_def):
    object.__init__(self)
    self.class_def_ = class_def
    self.out_ = StringIO()

  def Generate(self):
    pass
