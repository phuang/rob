// Copyright (c) 2013 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.
#ifndef ROB_MUTEX_PRIVATE_H_
#define ROB_MUTEX_PRIVATE_H_

#include <pthread.h>

namespace rob {

struct MutexPrivate {
    pthread_mutex_t mutex;
};

}  // namespace rob

#endif // ROB_MUTEX_PRIVATE_H_
