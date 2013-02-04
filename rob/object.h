// Copyright (c) 2013 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.
#ifndef ROB_OBJECT_H_
#define ROB_OBJECT_H_

#include <string>

#include "rob/meta_object.h"
#include "rob/object_defs.h"
#include "rob/rob_export.h"
#include "rob/variant.h"

namespace rob {

class Variant;

class ROB_EXPORT Object {
  R_OBJECT;
  R_PROPERTY(std::string object_name READ object_name WRITE set_object_name);

 public:
  Object() {}
  virtual ~Object() {}

  R_SLOT const std::string& object_name() const;
  R_SLOT void set_object_name(const std::string& name);

  bool set_property(const char* name, const Variant& prop);
  const Variant property(const char* name) const;

 private:
  std::string object_name_;
};

}  // namespace rob

#endif  // ROB_OBJECT_H_
