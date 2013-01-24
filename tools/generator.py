from cStringIO import StringIO

class Generator(object):
  def __init__(self, class_def):
    object.__init__(self)
    self.class_def_ = class_def
    self.out_ = []
    self.meta_strings_ = []
    self.meta_string_map_ = {}

  def Generate(self):
    out = self.out_
    clazz = self.class_def_
    METHOD_SIZE = 4
    method_count = len(clazz.slots) + len(clazz.signals)
    offset = 0
    out.append("static const unsigned int meta_data_%s[] = {" %s clazz.name)
    out.append("")
    out.append("  // content:")
    out.append("  0,  // classname")
    out.append("  %d, %d,  // methods" % (method_count, offset))
    offset += method_count * METHOD_SIZE
    out.append("  %d, %d,  // properties" % (len(clazz.properties), offset))
    out.append("  %d,  // signal count" % len(clazz.signals))

  def GenerateAllStrings(self):
    self.AddString(self.class_def.name)
    for slot in self.class_def.slots:
      self.AddString()

  def AddString(self, s):
    if s not in self.self.meta_strings_:
      self.self.meta_strings_.append(s)
