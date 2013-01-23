# Copyright (c) 2012 The Chromium Authors. All rights reserved.
#
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

{
  'includes': [
    'rob_tests.gypi'
  ],
  'targets': [
    {
      'target_name': 'rob',
      'type': 'static_library',
      'dependencies': [
      ],
      'include_dirs': [
        '..'
      ],
      'sources': [
        'condition.h',
        'condition.cc',
        'meta_object.cc',
        'meta_object.h',
        'meta_type.cc',
        'meta_type.h',
        'mutex.h',
        'mutex.cc',
        'mutex_private.h',
        'read_write_lock.cc',
        'read_write_lock.h',
        'rob.cc',
        'object.cc',
        'object.h',
        'object_defs.h',
        'thread.cc',
        'thread.h',
        'variant.cc',
        'variant.h',
      ]
    }
  ]
}

