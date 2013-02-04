// Copyright (c) 2013 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.
#include "rob/object.h"

namespace rob {

const std::string& Object::object_name() const {
  return object_name_;
}

void Object::set_object_name(const std::string& name) {
  object_name_ = name;
}

}  // namespace rob
