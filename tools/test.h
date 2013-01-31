#ifndef __TEST_H_
#define __TEST_H_
#include "rob/object.h"
namespace rob {

struct ClassA {
  R_OBJECT;
  R_PROPERTY(char* name READ name WRITE set_name);
  R_PROPERTY(int value READ getValue WRITE setValue);

  R_SLOT void HelloWorld();
  R_SLOT void HelloWorldC(int a, void* b);
  R_SLOT int getValue();
  R_SLOT rob::ClassA* getClass();
  R_SIGNAL void valueChanged(const char* name);

  const char* name();
  void set_name(const char* name);

  long long a;
  long long b;
  long long c;
};

const char* name = "\"Hello World\"";
}

#endif  // __TEST_H_
