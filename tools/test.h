#include <object>

#define A(x) a

#define B(x) \
    a \
    c

namespace rob {

struct ClassA : public Object {
  R_OBJECT
  R_PROPERTY(char* name READ name WRITE set_name)

  R_SLOT void HelloWorld();
  R_SLOT void HelloWorldC(int a, void* b);
  R_SLOT int getValue();
  R_SLOT rob::ClassA* getClass();
  R_SIGNAL void valueChanged(const char* name);
  R_PROPERTY(int value READ getValue WRITE setValue);

  const char* name();
  void set_name(const char* name)

  long long a;
  long long b;
  long long c;
};

const char* name = "\"Hello World\"";
}
