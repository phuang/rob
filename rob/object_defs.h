// Copyright (c) 2013 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.
#ifndef ROB_OBJECT_DEFS_H_
#define ROB_OBJECT_DEFS_H_

#define R_OBJECT \
 public: \
  virtual const MetaObject *meta_object() const; \
  virtual int meta_call(MetaObject::Call, int, void **); \
  virtual void* meta_cast(const char* name); \
 private: \
  static void static_meta_call(Object *, MetaObject::Call, int, void**); \
  static const MetaObject static_meta_object_;

#define R_SLOT
#define R_SIGNAL
#define R_PROPERTY(text)

#endif  // ROB_OBJECT_DEFS_H_
