// Copyright (c) 2013 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.
#include "rob/mutex.h"

#include "base/logging.h"
#include "rob/mutex_private.h"

namespace rob {

Mutex::Mutex() : d_(new MutexPrivate) {
  CHECK(pthread_mutex_init(&d_->mutex, NULL) == 0);
}

Mutex::~Mutex() {
  delete d_;
}

void Mutex::Lock() {
  CHECK(pthread_mutex_lock(&d_->mutex) == 0);
}

void Mutex::Unlock() {
  CHECK(pthread_mutex_unlock(&d_->mutex) == 0);
}

}  // namespace rob
