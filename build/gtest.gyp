# Copyright (c) 2012 The Chromium Authors. All rights reserved.
#
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

{
  'targets': [
    {
      'target_name': 'gtest',
      'type': 'static_library',
      'dependencies': [
      ],
      'include_dirs': [
        '../gtest',
        '../gtest/include',
      ],
      'direct_dependent_settings': {
        'include_dirs': [
          '../gtest/include',
        ],
        'cflags': [
          '-pthread',
        ],
        'ldflags': [
          '-pthread',
        ],
      },
      'sources': [
        '../gtest/src/gtest-all.cc',
        '../gtest/src/gtest_main.cc',
      ],
    }
  ]
}

