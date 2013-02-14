// Copyright (c) 2013 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.
#include "rob/meta_object.h"

#include <cstring>
#include <string>

namespace rob {

namespace {

struct MetaObjectPrivate {
  unsigned int class_name;
  unsigned int method_count;
  unsigned int method_offset;
  unsigned int property_count;
  unsigned int property_offset;
  unsigned int signal_count;
  unsigned int data[0];
};

inline const MetaObjectPrivate* _priv(const unsigned int* data) {
  return reinterpret_cast<const MetaObjectPrivate*>(data);
}

inline const char * _method_name(const MetaObject* m, int index) {
  if (index >=  _priv(m->data)->method_count || index < 0)
    return NULL;
  int i = _priv(m->data)->data[_priv(m->data)->method_offset + index * 4];
  return m->string_data + i;
}

inline const char * _property_name(const MetaObject* m, int index) {
  if (index >=  _priv(m->data)->property_count || index < 0)
    return NULL;
  int i = _priv(m->data)->data[_priv(m->data)->property_offset + index * 2];
  return m->string_data + i;
}

}  // namespace

const char* MetaObject::class_name() const {
  return string_data;
}

const char* MetaObject::super_class_name() const {
  return super_data ? super_data->class_name() : NULL;
}

int MetaObject::method_offset() const {
  int offset = 0;
  const MetaObject *m = super_data;
  while (m) {
    offset += _priv(m->data)->method_count;
    m = m->super_data;
  }
  return offset;
}

int MetaObject::property_offset() const {
  int offset = 0;
  const MetaObject *m = super_data;
  while (m) {
    offset += _priv(m->data)->property_count;
    m = m->super_data;
  }
  return offset;
}

int MetaObject::method_count() const {
  int offset = 0;
  const MetaObject *m = this;
  while (m) {
    offset += _priv(m->data)->method_count;
    m = m->super_data;
  }
  return offset;
}

int MetaObject::property_count() const {
  int offset = 0;
  const MetaObject *m = this;
  while (m) {
    offset += _priv(m->data)->property_count;
    m = m->super_data;
  }
  return offset;
}

int MetaObject::index_of_method(const char* name) const {
  std::string buf(name);
  size_t i = buf.find('.');

  if (i != std::string::npos) {
    std::string class_name = buf.substr(0,  i);
    std::string method_name = buf.substr(i + 1);
    const MetaObject *m = this;
    while (m) {
      if (class_name == m->string_data) {
        for (int i = 0;  i < _priv(m->data)->method_count; i++) {
          if (method_name == _method_name(m, i))
            return i + m->method_offset();
        }
      }
      m = m->super_data;
    }
  } else {
    std::string method_name = buf;
    const MetaObject *m = this;
    while (m) {
      for (int i = 0;  i < _priv(m->data)->method_count; i++) {
          if (method_name == _method_name(m, i))
            return i + m->method_offset();
      }
      m = m->super_data;
    }
  }
  return -1;
}

int MetaObject::index_of_property(const char* name) const {
  std::string buf(name);
  size_t i = buf.find('.');

  if (i != std::string::npos) {
    std::string class_name = buf.substr(0,  i);
    std::string property_name = buf.substr(i + 1);
    const MetaObject *m = this;
    while (m) {
      if (class_name == m->string_data) {
        for (int i = 0;  i < _priv(m->data)->property_count; i++) {
          if (property_name == _property_name(m, i))
            return i + m->property_offset();
        }
      }
      m = m->super_data;
    }
  } else {
    std::string property_name = buf;
    const MetaObject *m = this;
    while (m) {
      for (int i = 0;  i < _priv(m->data)->property_count; i++) {
          if (property_name == _property_name(m, i))
            return i + m->property_offset();
      }
      m = m->super_data;
    }
  }
  return -1;
}

MetaMethod MetaObject::method(int index) const {
  return MetaMethod();
}

const char* MetaObject::property_name(int index) const {
}

}  // namespace rob
