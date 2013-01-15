// Copyright (c) 2013 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.
#ifndef ROB_READ_WRITE_LOCK_H_
#define ROB_READ_WRITE_LOCK_H_

#include "base/basictypes.h"
#include "rob/rob_export.h"

namespace rob {

class Condition;
class Mutex;

struct ReadWriteLockPrivate;

class ROB_EXPORT ReadWriteLock {
 public:
  ReadWriteLock();
  ~ReadWriteLock();

  void LockForRead();
  void LockForWrite();
  void Unlock();

 private:
  ReadWriteLockPrivate* d_;

  DISALLOW_COPY_AND_ASSIGN(ReadWriteLock);
};

class ReadLocker {
 public:
  inline explicit ReadLocker(ReadWriteLock* lock);
  inline ~ReadLocker();

 private:
  ReadWriteLock* lock_;
  
  DISALLOW_COPY_AND_ASSIGN(ReadLocker);
};

class WriteLocker {
 public:
   inline explicit WriteLocker(ReadWriteLock* lock);
   inline ~WriteLocker();

 private:
  ReadWriteLock* lock_;
  
  DISALLOW_COPY_AND_ASSIGN(WriteLocker);
};

inline ReadLocker::ReadLocker(ReadWriteLock* lock) : lock_(lock) {
  lock_->LockForRead();
}

inline ReadLocker::~ReadLocker() {
  lock_->Unlock();
}

inline WriteLocker::WriteLocker(ReadWriteLock* lock) : lock_(lock) {
  lock_->LockForWrite();
}

inline WriteLocker::~WriteLocker() {
  lock_->Unlock();
}

}  // namespace rob

#endif // ROB_READ_WRITE_LOCK_H_
