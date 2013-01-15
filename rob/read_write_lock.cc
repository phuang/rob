// Copyright (c) 2013 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.
#include "rob/read_write_lock.h"

#include "base/logging.h"
#include "rob/condition.h"
#include "rob/mutex.h"

namespace rob {

struct ReadWriteLockPrivate {
  ReadWriteLockPrivate()
      : access_count(0),
        waiting_readers(0),
        waiting_writers(0) {}

  Mutex mutex;
  Condition reader_condition;
  Condition writer_condition;

  int access_count;
  int waiting_readers;
  int waiting_writers;
};

ReadWriteLock::ReadWriteLock() : d_(new ReadWriteLockPrivate()) {
}

void ReadWriteLock::LockForRead() {
  MutexLocker(&d_->mutex);

  while (d_->access_count < 0 || d_->waiting_writers > 0) {
    ++d_->waiting_readers;
    d_->reader_condition.Wait(&d_->mutex);
    --d_->waiting_readers;
  }
  ++d_->access_count;
}

void ReadWriteLock::LockForWrite() {
  MutexLocker(&d_->mutex);
  
  while (d_->access_count != 0) {
    ++d_->waiting_writers;
    d_->writer_condition.Wait(&d_->mutex);
    --d_->waiting_writers;
  }
  --d_->access_count;
}

void ReadWriteLock::Unlock() {
  MutexLocker(&d_->mutex);
  CHECK(d_->access_count != 0);

  if (d_->access_count > 0) {
    --d_->access_count;
  } else {
    ++d_->access_count;
  }

  if (!d_->access_count) {
    if (d_->waiting_writers) {
      d_->writer_condition.WakeOne();
    } else if (d_->waiting_readers) {
      d_->reader_condition.WakeAll();
    }
  }
}

ReadWriteLock::~ReadWriteLock() {
  delete d_;
}

}  // namespace rob
