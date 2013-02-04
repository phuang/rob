#include <string>

#include "gtest/include/gtest/gtest.h"
#include "rob/meta_type.h"
#include "rob/mutex.h"
#include "rob/variant.h"

namespace rob {

namespace {

void test_type(int type, const char* name, int size) {
  MetaType meta_type(type);
  ASSERT_TRUE(meta_type.IsValid());
  EXPECT_EQ(std::string(name), meta_type.name());
  EXPECT_EQ(size, meta_type.size());
}

template<typename T>
void test_create_destroy(int type, T v1, T v2) {
  T* p = static_cast<T*>(MetaType::Create(type, &v1));

  EXPECT_TRUE(p);
  EXPECT_EQ(v1, *p);
  
  v1 = v2;
  EXPECT_NE(v1, *p);
  
  MetaType::Destroy(type, p);
}

}

TEST(Core, MetaType) {
  MetaType::Initialize();

#define TEST_STATIC_TYPE(id, type) \
    test_type(MetaTypeId<type>::metatype_id(), #type, sizeof(type));
  FOR_EACH_STATIC_TYPE(TEST_STATIC_TYPE);

  test_type(MetaType::VOID, "void", 0);

  test_create_destroy(MetaType::BOOL, false, true);
  test_create_destroy(MetaType::INT, 100, 200);
  test_create_destroy(MetaType::UINT, 100u, 200u);
  test_create_destroy(MetaType::LONGLONG, 999999999ll, 88888888ll);
  test_create_destroy(MetaType::ULONGLONG, 88888888ull, 7777777ull);
  test_create_destroy(MetaType::DOUBLE, 3.1415926, 2.0001);
  test_create_destroy(MetaType::CHAR, 'a', 'b');
  test_create_destroy(MetaType::BYTE, 'c', 'd');
  test_create_destroy(MetaType::STRING,
      std::string("Hello"), std::string("World"));
  test_create_destroy(MetaType::POINTER,
      static_cast<const void*>("Hello"), static_cast<const void*>("World"));
}

TEST(Core, Variant) {
  Variant b(true);

  Variant s("Hello World");
  EXPECT_EQ("Hello World", s.value<const std::string>());
}

TEST(Thread, TestMutex) {
  Mutex m;

  MutexLocker locker(&m);
  {
    MutexUnlocker unlocker(&m);
  }
}

}  // namespace rob
