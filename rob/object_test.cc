#include "gtest/include/gtest/gtest.h"
#include "rob/object.h"
#include "rob/variant.h"

namespace rob {

TEST(Object, method) {
  Object obj;
  const MetaObject* m = obj.meta_object();
  EXPECT_TRUE(m != NULL);

  int i1 = m->index_of_method("object_name");
  int i2 = m->index_of_method("Object::object_name");
  int i3 = m->index_of_method("set_object_name");
  int i4 = m->index_of_method("Object::set_object_name");
  int i5 = m->index_of_method("AA::set_object_name");
  int i6 = m->index_of_method("set_object_name_aa");
  EXPECT_NE(i1, -1);
  EXPECT_EQ(i1, i2);
  EXPECT_NE(i3, -1);
  EXPECT_EQ(i3, i4);
  EXPECT_EQ(i5, -1);
  EXPECT_EQ(i6, -1);

}

TEST(DISABLED_Object, property) {
  Object obj;
  obj.set_property("object_name", Variant("object 1"));
  EXPECT_EQ("object 1", obj.object_name());
}

}  // namespace rob
