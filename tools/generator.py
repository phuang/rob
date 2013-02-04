import time

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
    out.append('  %d,       // classname' % AddString(clazz.name))
    out.append('  %d, %d,  // methods' % (n_method,
        offset if n_method else 0))
    offset += n_method * METHOD_SIZE
    out.append('  %d, %d,  // properties' % (n_property,
        offset if n_property else 0))
    out.append('  %d,       // signal count' % len(clazz.signals))

    def GenerateFunc(f):
      out.append('  %d, %d, %d, %d,' % (
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
        out.append('  %d, %d,' % (
          AddString(p.name),
          AddString(p.type),
        ))
    out.append('  %d,  //eod' % 0)

    out.append('};')
    out.append('')

    out.append('static const char meta_string_data_%s[] = {' % clazz.name)
    for s in meta_string_array:
      out.append('  "%s\\0"' % s)
    out.append('};')
    out.append('')

    return '\n'.join(out)

  def GenerateMetaObject(self, clazz, out):
    out.append('const MetaObject %s::static_meta_object_ = {' % clazz.name)
    if clazz.parent:
      out.append('  &%s::static_meta_object_,' % clazz.parent)
    else:
      out.append('  NULL,')
    out.append('  meta_string_data_%s,' % clazz.name)
    out.append('  meta_data_%s' % clazz.name)
    out.append('};')
    out.append('')

  def GenerateMetaFunc(self, clazz, out):
    # virtual const MetaObject* Class::meta_object() const
    out.append('const MetaObject* %s::meta_object() const {' % clazz.name)
    out.append('  return &static_meta_object_;')
    out.append('}')
    out.append('')

    # virtual void* Class::meta_cast(const char* class_name)
    out.append('void* %s::meta_cast(const char* class_name) {' % clazz.name)
    out.append('  if (!class_name) return 0;')
    out.append('  if (!strcmp(class_name, meta_string_data_%s))' % clazz.name)
    out.append('    return static_cast<void*>(const_cast<%s*>(this));' % clazz.name)
    if clazz.parent:
      out.append('  return %s::meta_cast(class_name);' % clazz.parent)
    else:
      out.append('  return NULL;')
    out.append('}')
    out.append('')

    # virtual int Class::meta_call(MetaObject::Call _c, int _id, void **_a)
    out.append('int %s::meta_call(MetaObject::Call _c, int _id, void **_a) {' % clazz.name)
    if clazz.parent:
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

    methods = clazz.signals + clazz.slots
    for i, f in enumerate(methods):
      out.append('        case %d: {' % i)
      GenerateFunctionCall(f)
      out.append('          break;')
      out.append('        }')
    out.append('      }');
    if methods:
      out.append('      _id -= %d;' % len(methods));
    out.append('      break;');
    out.append('    }');
    out.append('');

    # read property
    out.append('    case MetaObject::READ_PROPERTY: {')
    out.append('      switch(_id) {')
    for i, p in enumerate(clazz.properties):
      out.append('        case %d: {' % i)
      out.append('          %s* _v = reinterpret_cast<%s*>(_a[0]);' % (p.type, p.type))
      out.append('          *_v = %s::%s();' % (clazz.name, p.read))
      out.append('          break;')
      out.append('        }')
    out.append('      }')
    if clazz.properties:
      out.append('      _id -= %d;' % len(clazz.properties))
    out.append('      break;')
    out.append('    }')
    out.append('');

    # write property
    out.append('    case MetaObject::WRITE_PROPERTY: {')
    out.append('      switch(_id) {')
    for i, p in enumerate(clazz.properties):
      if not p.write:
        continue
      out.append('        case %d: {' % i)
      out.append('          const %s* _v = reinterpret_cast<%s*>(_a[1]);' % (p.type, p.type))
      out.append('          *%s::%s(*_v);' % (clazz.name, p.read))
      out.append('          break;')
      out.append('        }')
    out.append('      }')
    if clazz.properties:
      out.append('      _id -= %d;' % len(clazz.properties))
    out.append('      break;')
    out.append('    }')
    out.append('');

    # switch end
    out.append('  }');
    out.append('  return _id;')
    out.append('}')
    out.append('')

  def GenerateClass(self, clazz, out):
    if clazz.namespace:
      out.append('namespace %s {' % clazz.namespace)
      out.append('')
    
    self.GenerateMetaData(clazz, out)
    self.GenerateMetaObject(clazz, out)
    self.GenerateMetaFunc(clazz, out)
    
    if clazz.namespace:
      out.append('}  // namespace %s' % clazz.namespace)
      out.append('')

  def GenerateHeader(self, filename, out):
    out.append('/* Meta object code from reading C++ file \'%s\'' % filename)
    out.append(' * Created: %s' % time.asctime())
    out.append(' *      by: Chrome Meta Object Compiler version %s' % '0.0.1')
    out.append(' *  WARNING! All changes made in this file will be lost!')
    out.append(' */')
    out.append('#include "%s"' % filename)
    out.append('')
    out.append('#include <cstring>')
    out.append('')
    out.append('using rob::MetaObject;')

  def Generate(self, filename, classes):
    out = []

    self.GenerateHeader(filename, out)

    for clazz in classes:
      self.GenerateClass(clazz, out)

    return '\n'.join(out)
