class Generator(object):
  def __init__(self, class_def):
    object.__init__(self)
    self.class_def_ = class_def
    self.out_ = []
    self.meta_string_array_ = []
    self.meta_string_map_ = {}
    self.meta_string_last_ = 0

  def Generate(self):
    self.GenerateMetaData(self.out_)
    return '\n'.join(self.out_)

  def GenerateMetaData(self, out):
    clazz = self.class_def_
    METHOD_SIZE = 4
    n_method = len(clazz.slots) + len(clazz.signals)
    n_property = len(clazz.properties)
    offset = 0
    out.append('static const unsigned int meta_data_%s[] = {' % clazz.name)
    out.append('  // content:')
    out.append('  %3d,       // classname' % self.AddString(clazz.name))
    out.append('  %3d, %3d,  // methods' % (n_method,
        offset if n_method else 0))
    offset += n_method * METHOD_SIZE
    out.append('  %3d, %3d,  // properties' % (n_property,
        offset if n_property else 0))
    out.append('  %3d,       // signal count' % len(clazz.signals))
    out.append('')

    def GenerateFunc(f):
      out.append('  %3d, %3d, %3d, %3d,' % (
        self.AddString(s.name),
        self.AddString(','.join([t.name for t, n in s.params])),
        self.AddString(','.join([n for t, n in s.params])),
        self.AddString(s.type.name if s.type.name != 'void' else ''),
      ))
    if clazz.signals:
      out.append('  // signals: name, signature, parameters, type')
      for s in clazz.signals:
        GenerateFunc(s)
      out.append('')

    if clazz.slots:
      out.append('  // slot: name, signature, parameters, type')
      for s in clazz.slots:
        GenerateFunc(s)
      out.append('')

    if clazz.properties:
      out.append('  // property: name, type')
      for p in clazz.properties:
        out.append('  %3d, %3d,' % (
          self.AddString(p.name),
          self.AddString(p.type.name),
        ))
      out.append('')
    out.append('  %3d,  //eod' % 0)

    out.append('};')
    out.append('')

    out.append('static const char meta_stringdata_%s[] = {' % clazz.name)
    for s in self.meta_string_array_:
      out.append('  "%s\\0"' % s)
    out.append('};')
    out.append('')

    return '\n'.join(out)

  def GenerateAllStrings(self):
    self.AddString(self.class_def.name)
    for slot in self.class_def.slots:
      self.AddString()

  def AddString(self, s):
    if s not in self.meta_string_map_:
      self.meta_string_array_.append(s)
      self.meta_string_map_[s] = self.meta_string_last_
      self.meta_string_last_ += len(s) + 1
    return self.meta_string_map_[s]

