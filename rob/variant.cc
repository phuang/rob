// Copyright (c) 2013 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.
#include "rob/variant.h"

#include <stdlib.h>
#include <string.h>

#include "base/logging.h"

namespace rob {

Variant::Variant() {
  type_ = INVALID;
}

Variant::~Variant() {
  Clear();
}

Variant::Variant(Type type) : type_(type) {
  memset(&data_, 0, sizeof(data_));
}

Variant::Variant(int type_id, const void* copy)  {
}

Variant::Variant(const Variant& other) {
  *this = other;
}

Variant::Variant(bool b) : type_(BOOL) {
  data_.b = b;
}

Variant::Variant(int i) : type_(INT) {
  data_.i = i;
}

Variant::Variant(unsigned int ui) : type_(UINT) {
  data_.ui = ui;
}

Variant::Variant(long long ll) : type_(LONGLONG) {
  data_.ll = ll;
}

Variant::Variant(unsigned long long ull) : type_(ULONGLONG) {
  data_.ull = ull;
}

Variant::Variant(double d) : type_(DOUBLE) {
  data_.d = d;
}

Variant::Variant(char c) : type_(CHAR) {
  data_.c = c;
}

Variant::Variant(unsigned char uc) : type_(BYTE) {
  data_.uc = uc;
}

Variant::Variant(const std::string& s) : type_(STRING) {
  data_.p = new std::string(s);
}

Variant::Variant(const char* s) : type_(STRING) {
  data_.p = new std::string(s);
}

Variant& Variant::operator=(const Variant& other) {
  if (this != &other) {
    Clear();
    type_ = other.type_;
    switch(type_) {
      case STRING:
        delete static_cast<std::string*>(data_.p);
        data_.p = new std::string(
            *static_cast<const std::string*>(other.data_.p));
        break;
      default:
        data_ = other.data_;
        break;
    }
  }
  return *this;
}

void Variant::Clear() {
  switch(type_) {
    case STRING:
      delete static_cast<std::string*>(data_.p);
      break;
    default:
      break;
  }
}

}  // namespace rob
