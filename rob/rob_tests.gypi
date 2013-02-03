# Copyright (c) 2012 The Chromium Authors. All rights reserved.
#
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

{
  'targets': [
    {
      'target_name': 'rob_unittests',
      'type': 'executable',
      'dependencies': [
        'rob',
        '../build/gtest.gyp:gtest',
      ],
      'include_dirs': [
        '..'
      ],
      'sources': [
        "rob_unittest.cc"
      ]
    }
  ]
}
