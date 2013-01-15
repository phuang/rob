// Copyright (c) 2013 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.
#ifndef ROB_META_TYPE_H_
#define ROB_META_TYPE_H_

#include <string>

#include "rob/rob_export.h"

namespace rob {

#define FOR_EACH_STATIC_TYPE(F) \
    F(BOOL, bool) \
    F(INT, int) \
    F(UINT, unsigned int) \
    F(LONGLONG, long long) \
    F(ULONGLONG, unsigned long long) \
    F(DOUBLE, double) \
    F(CHAR, char) \
    F(BYTE, unsigned char) \
    F(POINTER, void*)

class ROB_EXPORT MetaType {
 public:
  enum Type {
    UNKNOWN_TYPE = -1,
    VOID = 0,  // void
    BOOL = 1,  // bool
    INT = 2,  // int
    UINT = 3,  // unsigned int
    LONGLONG = 4,  // long long
    ULONGLONG = 5,  // unsigned long long
    DOUBLE = 6,  // double
    CHAR = 7,  // char
    BYTE = 8,  // unsigned char
    POINTER = 9,  // void *.
    STRING = 10,  // A std::string in UTF8 format.
    USER = 256,
  };

  enum TypeFlag {
    NEEDS_CONSTRUCTION = (1 << 0),
    NEEDS_DESTRUCTION = (1 << 1),
  };

  typedef void (*Deleter)(void*);
  typedef void* (*Creator)(const void *);

 public:
  // static functions
  static void Initialize();
  static int RegisterType(const char* name,
                          Creator creator,
                          Deleter deleter);
  static bool IsRegistered(int type);
  static int TypeFromName(const char* name);
  static const char* TypeName(int type);
  static void* Create(int type, const void* copy);
  static void Destroy(int type, void* data);

  // member functions
  inline MetaType();
  explicit MetaType(int type);
  inline ~MetaType();
  
  inline bool IsValid() const;
  inline const char* name() const;
  inline unsigned int size() const;

  inline void* Create(const void* copy) const;
  inline void Destroy(void* data) const;
 
 private:
  // static functions
  static void RegisterStaticType(int type,
                                 const char* name,
                                 Creator creator,
                                 Deleter deleter,
                                 unsigned int size);
  static MetaType TypeInfo(int type);

  // member functions
  inline MetaType(int type,
                  const std::string& name,
                  Creator creator,
                  Deleter deleter,
                  unsigned int size);
  inline MetaType(const MetaType& other);
  inline MetaType& operator=(const MetaType& other);


  int type_id_;
  std::string name_;
  Creator creator_;
  Deleter deleter_;
  unsigned int size_;
};

template<typename T>
struct MetaTypeId {
  enum { defined = MetaTypeId<T>::Defined, is_built_in = false };
  static inline int metatype_id() { return MetaTypeId<T>::metatype_id(); }
};

inline MetaType::~MetaType() {
}

inline bool MetaType::IsValid() const {
  return type_id_ != UNKNOWN_TYPE;
}

inline const char*  MetaType::name() const {
  return name_.c_str();
}

inline unsigned int MetaType::size() const {
  return size_;
}

inline void* MetaType::Create(const void* copy) const {
  return creator_(copy);
}

inline void MetaType::Destroy(void* data) const {
  deleter_(data);
}

}  // namespace rob

#define DECLARE_BUILTIN_METATYPE(METATYPE_ID, TYPE) \
  namespace rob { \
    template<> struct MetaTypeId<TYPE> { \
      enum { defined = 1, is_built_in = true }; \
      static inline int metatype_id() { return MetaType::METATYPE_ID; } \
    }; \
  }  // namespace rob


// Define built in types.
FOR_EACH_STATIC_TYPE(DECLARE_BUILTIN_METATYPE);
DECLARE_BUILTIN_METATYPE(STRING, std::string);
DECLARE_BUILTIN_METATYPE(STRING, const std::string);

#endif  // ROB_META_TYPE_H_
