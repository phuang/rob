// Copyright (c) 2013 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.
#ifndef ROB_MUTEX_H_
#define ROB_MUTEX_H_

#include "base/basictypes.h"
#include "rob/rob_export.h"

namespace rob {

class Condition;

struct MutexPrivate;

class ROB_EXPORT Mutex {
 public:
  Mutex();
  ~Mutex();

  void Lock();
  void Unlock();

 private:
  friend class Condition;
  MutexPrivate* d_;

  DISALLOW_COPY_AND_ASSIGN(Mutex);
};

class ROB_EXPORT MutexLocker {
 public:
  inline explicit MutexLocker(Mutex* m) : mutex_(m) {
    mutex_->Lock();
  }

  inline ~MutexLocker() {
    mutex_->Unlock();
  }

 private:
  Mutex* mutex_;

  DISALLOW_COPY_AND_ASSIGN(MutexLocker);
};

class ROB_EXPORT MutexUnlocker {
 public:
  inline explicit MutexUnlocker(Mutex* m) : mutex_(m) {
    mutex_->Unlock();
  }

  inline ~MutexUnlocker() {
    mutex_->Lock();
  }

 private:
  Mutex* mutex_;

  DISALLOW_COPY_AND_ASSIGN(MutexUnlocker);
};

}  // namespace rob

#endif // ROB_MUTEX_H_
