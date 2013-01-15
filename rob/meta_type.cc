// Copyright (c) 2013 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.
#include "rob/meta_type.h"

#include <stdlib.h>
#include <string.h>

#include <map>
#include <string>
#include <vector>

#include "base/logging.h"
#include "rob/read_write_lock.h"

namespace rob {

namespace {

struct PrivateData {
  PrivateData() : meta_types(MetaType::USER) {
  }

  ReadWriteLock lock;
  std::vector<const MetaType*> meta_types;
  std::map<std::string, const MetaType*> meta_type_map;
};

PrivateData *priv = NULL;

template<typename T>
void* default_creator(const void* copy) {
  T* data = copy ? new T(*static_cast<const T*>(copy)) : new T();
  return static_cast<void*>(data);
}

template<typename T>
void default_deleter(void* data) {
  DCHECK(data);
  delete static_cast<T*>(data);
}

}  // namespace

// static
void MetaType::Initialize() {
  if (!priv) {
    priv = new PrivateData();

    WriteLocker lock(&priv->lock);
    
    // register primitive types
#define REGISTER_STATIC_TYPE(id, type) \
    RegisterStaticType(id, #type, \
        default_creator<type>, default_deleter<type>, sizeof(type));

    FOR_EACH_STATIC_TYPE(REGISTER_STATIC_TYPE);
    
    RegisterStaticType(STRING, "std::string",
        default_creator<std::string>, default_deleter<std::string>, 0);
    RegisterStaticType(VOID, "void", NULL, NULL, 0);
    
  }
}

// static
int MetaType::RegisterType(const char* name,
                           Creator creator,
                           Deleter deleter) {
}

// static
void MetaType::RegisterStaticType(int type,
                                  const char* name,
                                  Creator creator,
                                  Deleter deleter,
                                  unsigned int size) {
  DCHECK(!priv->meta_types[type]);
  DCHECK(!priv->meta_type_map[name]);

  MetaType* meta_type = new MetaType(type, name, creator, deleter, size);
  priv->meta_types[type] = meta_type;
  priv->meta_type_map[name] = meta_type;
}

// static
bool MetaType::IsRegistered(int type) {
  return MetaType::TypeInfo(type).type_id_;
}

// static
int MetaType::TypeFromName(const char* name) {
  ReadLocker lock(&priv->lock);
  std::map<std::string, const MetaType*>::const_iterator it =
    priv->meta_type_map.find(name);
  return it != priv->meta_type_map.end() ? it->second->type_id_ : UNKNOWN_TYPE;
}

// static
const char* MetaType::TypeName(int type) {
  return MetaType::TypeInfo(type).name();
}

// static
MetaType MetaType::TypeInfo(int type) {
  ReadLocker lock(&priv->lock);
  if (type > UNKNOWN_TYPE && type < priv->meta_types.size()) {
    const MetaType *meta_type = priv->meta_types[type];
    if (meta_type)
      return *meta_type;
  }
  return MetaType(UNKNOWN_TYPE, "", NULL, NULL, 0);
}

// static
void* MetaType::Create(int type, const void* copy) {
  MetaType meta_type = MetaType::TypeInfo(type);
  return meta_type.Create(copy);
}

// static
void MetaType::Destroy(int type, void* data) {
  MetaType meta_type = MetaType::TypeInfo(type);
  return meta_type.Destroy(data);
}

inline MetaType::MetaType()
    : type_id_(UNKNOWN_TYPE),
      name_(""), 
      creator_(NULL),
      deleter_(NULL),
      size_(0) {}

MetaType::MetaType(int type)
    : type_id_(type) {
  *this = MetaType::TypeInfo(type);
}

inline MetaType::MetaType(int type,
                          const std::string& name,
                          Creator creator,
                          Deleter deleter,
                          unsigned int size)
    : type_id_(type),
      name_(name),
      creator_(creator),
      deleter_(deleter),
      size_(size) {}

inline MetaType::MetaType(const MetaType& other)
    : type_id_(other.type_id_),
      name_(other.name_),
      creator_(other.creator_),
      deleter_(other.deleter_),
      size_(other.size_) {}

inline MetaType& MetaType::operator=(const MetaType& other) {
  type_id_ = other.type_id_;
  name_ = other.name_;
  creator_ = other.creator_;
  deleter_ = other.deleter_;
  size_ = other.size_;
}

}  // namespace rob
