// Copyright (c) 2013 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.
#ifndef ROB_VARIANT_H_
#define ROB_VARIANT_H_

#include <string>

#include "rob/meta_type.h"
#include "rob/rob_export.h"

namespace rob {

class ROB_EXPORT Variant {
 public:
  enum Type {
    INVALID = MetaType::UNKNOWN_TYPE,
    BOOL = MetaType::BOOL,
    INT = MetaType::INT,
    UINT = MetaType::UINT,
    LONGLONG = MetaType::LONGLONG,
    ULONGLONG = MetaType::ULONGLONG,
    DOUBLE = MetaType::DOUBLE,
    CHAR = MetaType::CHAR,
    BYTE = MetaType::BYTE,
    STRING = MetaType::STRING,
  };

  Variant();
  ~Variant();

  Variant(Type type);
  Variant(int type_id, const void* copy);
  Variant(const Variant& other);

  Variant(bool b);
  Variant(int i);
  Variant(unsigned int ui);
  Variant(long long ll);
  Variant(unsigned long long ull);
  Variant(double d);
  Variant(char c);
  Variant(unsigned char uc);  // byte
  Variant(const std::string& s);
  Variant(const char* s);

  bool operator==(const Variant& other);
  Variant& operator=(const Variant& other);

  template<typename T>
  T value() const;

  union Data {
    bool b;
    int i;
    unsigned ui;
    long long ll;
    unsigned long long ull;
    double d;
    char c;
    unsigned char uc;
    void* p;
  };

 private:
  void Clear();

  int type_;
  Data data_;
};

template<typename T>
T Variant::value() const {
  if (MetaTypeId<T>::metatype_id() != type_)
    return T();
  if (type_ < STRING)
    return *reinterpret_cast<const T*>(&data_);
  return *static_cast<const T*>(data_.p);
}

}  // namespace rob

#endif // ROB_VARIANT_H_
