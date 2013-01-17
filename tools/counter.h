#include <QObject>

#define A(x) a

#define B(x) \
    a \
    c

namespace rob {

struct ClassA {
  R_OBJECT;
  R_SLOT void HelloWorld();
  R_SLOT void HelloWorldC(int a, void* b);
  R_SLOT int getValue();
  R_SLOT const long long* getValue();
  long long a;
  long long b;
  long long c;
};

class Counter : public QObject
{
  R_OBJECT
 public:
  enum CounterFlags {
    One = 1,
    Two = 2,
  };
  Q_ENUMS(CounterFlags);
  Q_FLAGS(CounterFlags);

 
 public:
  struct A valueA() const { return m_a; }
  const struct A& valueAR() const { return m_a; }
  const struct A* valueAP() const { return &m_a; }
  long long valueLL() const { return (long long) m_value; }
  int value() const { return m_value; }
  virtual void setValue(int value);

  void setFlags(CounterFlags flags) { m_flags = flags; }
 
 signals:
  void valueChanged(int newValue);
 
 private:
  Q_PROPERTY(int value READ value WRITE setValue DESIGNABLE true);
  int m_value;
  struct A m_a;
  CounterFlags m_flags;
};

class CounterEx : public Counter
{
  R_OBJECT
 public:
  virtual void setValue(int newValue);
};

class AA: public QObject {
  R_OBJECT
};

const char* name = "\"Hello World\"";

}
