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
  R_OBJECT
 public:
  Object();
  virtual ~Object();

  void set_object_name(const char* name);
  const std::string& object_name() const;
  bool set_property(const char* name, const Variant& prop);
  const Variant& property(const char* name) const;

 protected:
  virtual int MetaCall(int id, void** args);

 private:

};

}  // namespace rob

#endif  // ROB_OBJECT_H_
