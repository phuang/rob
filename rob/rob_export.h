// Copyright (c) 2012 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#ifndef ROB_ROB_EXPORT_H_
#define ROB_ROB_EXPORT_H_

#if defined(COMPONENT_BUILD)
#if defined(WIN32)

#if defined(ROB_IMPLEMENTATION)
#define ROB_EXPORT __declspec(dllexport)
#define ROB_EXPORT_PRIVATE __declspec(dllexport)
#else
#define ROB_EXPORT __declspec(dllimport)
#define ROB_EXPORT_PRIVATE __declspec(dllimport)
#endif  // defined(ROB_IMPLEMENTATION)

#else  // defined(WIN32)
#if defined(ROB_IMPLEMENTATION)
#define ROB_EXPORT __attribute__((visibility("default")))
#define ROB_EXPORT_PRIVATE __attribute__((visibility("default")))
#else
#define ROB_EXPORT
#define ROB_EXPORT_PRIVATE
#endif  // defined(ROB_IMPLEMENTATION)
#endif

#else  // defined(COMPONENT_BUILD)
#define ROB_EXPORT
#define ROB_EXPORT_PRIVATE
#endif

#endif  // ROB_ROB_EXPORT_H_
