// Copyright (c) 2013 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.
#ifndef ROB_OBJECT_DEFS_H_
#define ROB_OBJECT_DEFS_H_

#define R_OBJECT \
 public: \
  static const MetaObject static_meta_object_; \
  virtual const MetaObject *meta_object() const; \
  virtual int ROB_MetaCall(MetaObject::Call, int, void **); \
 private: \
  static void ROB_StaticMetaCall(Object *, MetaObject::Call, int, void**);

#define R_SLOT
#define R_SIGNAL
#define R_PROPERTY(text)

#endif  // ROB_OBJECT_DEFS_H_
