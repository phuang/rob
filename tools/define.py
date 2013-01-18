from cStringIO import StringIO

class TypeDef(object):
  def __init__(self, name):
    object.__init__(self)
    self.name = name

  def __str__(self):
    return self.name

  def __repr__(self):
    return 'TypeDef[%s]' % self.__str__()

class FunctionDef(object):
  def __init__(self, name, static, virtual, type, params):
    object.__init__(self)
    self.name = name
    self.static = static
    self.virtual = virtual
    self.type = type
    self.params = params

  def __str__(self):
    return '%s %s (%s)' % (self.type, self.name,
        self.params if self.params else 'void')

  def __repr__(self):
    return 'FunctionDef[%s]' % self.__str__()


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

  def get_full_name(self):
    if self.namespace:
      return "%s::%s" % (self.namespace, self.name)
    return self.name

  def __str__(self):
    out = StringIO()
    if not self.parent:
      print >> out, "class %s {" % self.get_full_name()
    else:
      print >> out, "class %s : %s %s {" % \
          (self.get_full_name(), self.parentaccess_.lower(), self.parent)

    for slot in self.slots:
      print >> out, "  %s" % slot
    print >> out, "};"
    return out.getvalue()

  def __repr__(self):
    return 'ClassDef[%s]' % self.__str__()

class NamespaceDef(object):
  def __init__(self, name, begin, end):
    object.__init__(self)
    self.name = name
    self.begin = begin
    self.end = end
  
  def __str__(self):
    return self.name

  def __repr__(self):
    return 'NamespaceDef[%s]' % self.__str__()
