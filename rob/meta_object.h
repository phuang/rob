// Copyright (c) 2013 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.
#ifndef ROB_META_OBJECT_H_
#define ROB_META_OBJECT_H_

#include <string>

#include "rob/rob_export.h"
#include "rob/variant.h"

namespace rob {

class MetaObject;
class Object;

class ROB_EXPORT MetaMethod {
 public:
  const char* method_signature() const;
  const char* name() const;
  int returnType() const;
  int parameter_count() const;
  int parameter_type(int index) const;
  bool invoke(Object *object);

 private:
  const MetaObject* meta_object_;
  unsigned int handle_;
};

struct ROB_EXPORT MetaObject {
  enum Call {
    INVOKE_META_METHOD,
    READ_PROPERTY,
    WRITE_PROPERTY,
    INDEX_OF_METHOD,
  };

  const char* class_name() const;
  const char* super_class_name() const;

  int method_offset() const;
  int property_offset() const;

  int method_count() const;
  int property_count() const;

  int index_of_method(const char* name) const;
  int index_of_property(const char* name) const;

  const MetaObject* super_data;
  const char* string_data;
  const unsigned int* data;

};

}  // namespace rob

#endif  // ROB_META_OBJECT_H_
