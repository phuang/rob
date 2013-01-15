// Copyright (c) 2013 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.
#include "rob/condition.h"

#include "base/logging.h"

#include "rob/mutex.h"
#include "rob/mutex_private.h"

namespace rob {

struct ConditionPrivate {
  pthread_cond_t cond;
};

Condition::Condition() : d_(new ConditionPrivate) {
  CHECK(pthread_cond_init(&d_->cond, NULL) == 0);
}

Condition::~Condition() {
  CHECK(pthread_cond_destroy(&d_->cond) == 0);
  delete d_;
}

void Condition::Wait(Mutex* locked_mutex) {
  CHECK(pthread_cond_wait(&d_->cond, &locked_mutex->d_->mutex) == 0);
}

void Condition::WakeOne() {
  CHECK(pthread_cond_signal(&d_->cond) == 0);
}

void Condition::WakeAll() {
  CHECK(pthread_cond_broadcast(&d_->cond) == 0);
}

}  // namespace rob
