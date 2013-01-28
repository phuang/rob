class Generator(object):
  def __init__(self):
    object.__init__(self)

  def GenerateMetaData(self, clazz, out):
    METHOD_SIZE = 4
    n_method = len(clazz.slots) + len(clazz.signals)
    n_property = len(clazz.properties)
    offset = 0

    meta_string_array = []
    meta_string_map = {}
    # Have to use an array, so the nested function can access it
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

    def GenerateFunc(f):
      out.append('  %3d, %3d, %3d, %3d,' % (
        AddString(s.name),
        AddString(','.join([t for t, n in s.params])),
        AddString(','.join([n for t, n in s.params])),
        AddString(s.type if s.type != 'void' else ''),
      ))

    if clazz.signals:
      out.append('  // signals: name, signature, parameters, type')
      for s in clazz.signals:
        GenerateFunc(s)

    if clazz.slots:
      out.append('  // slot: name, signature, parameters, type')
      for s in clazz.slots:
        GenerateFunc(s)

    if clazz.properties:
      out.append('  // property: name, type')
      for p in clazz.properties:
        out.append('  %3d, %3d,' % (
          AddString(p.name),
          AddString(p.type),
        ))
    out.append('  %3d,  //eod' % 0)

    out.append('};')
    out.append('')

    out.append('static const char meta_string_data_%s[] = {' % clazz.name)
    for s in meta_string_array:
      out.append('  "%s\\0"' % s)
    out.append('};')
    out.append('')

    return '\n'.join(out)

  def GenerateMetaObject(self, clazz, out):
    out.append('const MetaObject %s::static_meta_object = {' % clazz.name)
    out.append('  &%s::static_meta_object,' % clazz.parent)
    out.append('  meta_string_data_%s,' % clazz.name)
    out.append('  meta_data_%s' % clazz.name)
    out.append('};')
    out.append('')

  def GenerateMetaFunc(self, clazz, out):
    # virtual const MetaObject* Class::meta_object() const
    out.append('const MetaObject* %s::meta_object() const {' % clazz.name)
    out.append('  return &static_meta_object;')
    out.append('}')
    out.append('')

    # virtual void* Class::meta_cast(const char* class_name)
    out.append('void* %s::meta_cast(const char* class_name) {' % clazz.name)
    out.append('  if (!class_name) return 0;')
    out.append('  if (!strcmp(class_name, meta_string_data_%s))' % clazz.name)
    out.append('    return static_cast<void*>(const_cast<%s*>(this));' % clazz.name)
    out.append('  return %s::meta_cast(class_name);' % clazz.parent)
    out.append('}')
    out.append('')

    # virtual int Class::meta_call(MetaObject::Call _c, int _id, void **_a)
    out.append('int %s::meta_call(MetaObject::Call _c, int _id, void **_a) {' % clazz.name)
    if clazz.name != 'Object':
      out.append('  _id = %s::meta_call(_c, _id, _a);' % clazz.parent)
      out.append('  if (_id < 0) return _id;')

    out.append('  switch(_c) {')

    # invoke meta method
    out.append('    case MetaObject::INVOKE_META_METHOD: {')
    out.append('      switch(_id) {')
    def GenerateFunctionCall(func):
      args = ['              *reinterpret_cast<%s*>(_a[%d])' % (t, i + 1)
          for i, (t, n) in enumerate(func.params)]
      prefix = ''
      if func.type != 'void':
        out.append('          %s* _r = reinterpret_cast<%s*>(_a[0]);' % (func.type, func.type))
        prefix = '*_r = '
      if args:
        out.append('          %s%s::%s(' % (prefix, clazz.name, func.name))
        out.append('%s);' % ',\n'.join(args))
      else:
        out.append('          *_r = %s::%s();' % (clazz.name, func.name))

    i = 0
    for f in clazz.signals:
      out.append('        case %d: {' % i)
      GenerateFunctionCall(f)
      out.append('          break;')
      out.append('        }')
      i += 1
    for f in clazz.slots:
      out.append('        case %d: {' % i)
      GenerateFunctionCall(f)
      out.append('          break;')
      out.append('        }')
      i += 1
    out.append('      }');
    out.append('      _id -= %d;' % i);
    out.append('      break;');
    out.append('    }');
    out.append('');

    # read property
    i = 0
    out.append('    case MetaObject::READ_PROPERTY: {')
    out.append('      switch(_id) {')
    for p in clazz.properties:
      out.append('        case %d: {' % i)
      out.append('          %s* _v = reinterpret_cast<%s*>(_a[0]);' % (p.type, p.type))
      out.append('          *_v = %s::%s();' % (clazz.name, p.read))
      out.append('          break;')
      out.append('        }')
      i += 1
    out.append('      }')
    out.append('      _id -= %d;' % i)
    out.append('      break;')
    out.append('    }')
    out.append('');

    # write property
    i = 0
    out.append('    case MetaObject::WRITE_PROPERTY: {')
    out.append('      switch(_id) {')
    for p in clazz.properties:
      if not p.write:
        i += 1
        continue
      out.append('        case %d: {' % i)
      out.append('          const %s* _v = reinterpret_cast<%s*>(_a[1]);' % (p.type, p.type))
      out.append('          *%s::%s(*_v);' % (clazz.name, p.read))
      out.append('          break;')
      out.append('        }')
      i += 1
    out.append('      }')
    out.append('      _id -= %d;' % i)
    out.append('      break;')
    out.append('    }')
    out.append('');

    # switch end
    out.append('  }');
    out.append('  return _id;')
    out.append('}')
    out.append('')

  def Generate(self, clazz):
    out = []
    self.GenerateMetaData(clazz, out)
    self.GenerateMetaObject(clazz, out)
    self.GenerateMetaFunc(clazz, out)
    return '\n'.join(out)



