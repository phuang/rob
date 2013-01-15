// Copyright (c) 2013 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.
#ifndef ROB_CONDITION_H_
#define ROB_CONDITION_H_

#include "rob/rob_export.h"

namespace rob {

class Mutex;

struct ConditionPrivate;

class ROB_EXPORT Condition {
 public:
  Condition();
  ~Condition();

  void Wait(Mutex* locked_mutex);
  void WakeOne();
  void WakeAll();

 private:
  ConditionPrivate* d_;
};

}  // namespace rob

#endif // ROB_CONDITION_H_
