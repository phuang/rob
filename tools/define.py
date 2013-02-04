from cStringIO import StringIO

class TypeDef(object):
  def __init__(self, name, is_const, is_ref):
    object.__init__(self)
    self.name = name
    self.is_const = is_const
    self.is_ref = is_ref

  def is_void(self):
    return self.name == 'void'

  def tostring_with_const(self):
    if self.is_const:
      return "const %s" % self.__str__()
    return self.__str__()

  def __str__(self):
    return self.name

  def __len__(self):
    return len(self.__str__())

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
    params = [(str(t) + ' ' + n if n else str(t)) for t, n in self.params]
    return '%s %s (%s)' % (self.type, self.name,
        ', '.join(params) if params else 'void')

  def __repr__(self):
    return 'FunctionDef[%s]' % self.__str__()

class PropertyDef(object):
  def __init__(self, name, type, read, write):
    object.__init__(self)
    self.name = name
    self.type = type
    self.read = read
    self.write = write

  def __str__(self):
    return '%s %s' % (self.type, self.name)

  def __repr__(self):
    return 'PropertyDef[%s]' % self.__str__()

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
      print >> out, "  slot %s;" % slot
    for signal in self.signals:
      print >> out, "  signal %s;" % signal
    for prop in self.properties:
      print >> out, "  property %s %s { %s, %s};" % (prop.type, prop.name, prop.read, prop.write)
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
