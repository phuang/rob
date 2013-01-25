class Generator(object):
  def __init__(self):
    object.__init__(self)

  def Generate(self, clazz):
    out = []
    self.GenerateMetaData(clazz, out)
    return '\n'.join(out)

  def GenerateMetaData(self, clazz, out):
    METHOD_SIZE = 4
    n_method = len(clazz.slots) + len(clazz.signals)
    n_property = len(clazz.properties)
    offset = 0

    meta_string_array = []
    meta_string_map = {}
    meta_string_offset = [0]

    def AddString(s):
      if s not in meta_string_map:
        meta_string_array.append(s)
        meta_string_map[s] = meta_string_offset[0]
        meta_string_offset[0] += len(s) + 1
      return meta_string_map[s]

    out.append('static const unsigned int meta_data_%s[] = {' % clazz.name)
    out.append('  // content:')
    out.append('  %3d,       // classname' % AddString(clazz.name))
    out.append('  %3d, %3d,  // methods' % (n_method,
        offset if n_method else 0))
    offset += n_method * METHOD_SIZE
    out.append('  %3d, %3d,  // properties' % (n_property,
        offset if n_property else 0))
    out.append('  %3d,       // signal count' % len(clazz.signals))
    out.append('')

    def GenerateFunc(f):
      out.append('  %3d, %3d, %3d, %3d,' % (
        AddString(s.name),
        AddString(','.join([t.name for t, n in s.params])),
        AddString(','.join([n for t, n in s.params])),
        AddString(s.type.name if s.type.name != 'void' else ''),
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
          AddString(p.name),
          AddString(p.type.name),
        ))
      out.append('')
    out.append('  %3d,  //eod' % 0)

    out.append('};')
    out.append('')

    out.append('static const char meta_stringdata_%s[] = {' % clazz.name)
    for s in meta_string_array:
      out.append('  "%s\\0"' % s)
    out.append('};')
    out.append('')

    return '\n'.join(out)

  def GenerateAllStrings(self):
    self.AddString(self.class_def.name)
    for slot in self.class_def.slots:
      self.AddString()


