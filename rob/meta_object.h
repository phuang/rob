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

class ROB_EXPORT MetaObject {
 public:
  enum Call {
    INVOKE_META_METHOD,
    READ_PROPERTY,
    WRITE_PROPERTY,
    INDEX_OF_METHOD,
  };
  MetaObject();
  virtual ~MetaObject();

 protected:

 private:

};

}  // namespace rob

#endif  // ROB_META_OBJECT_H_
