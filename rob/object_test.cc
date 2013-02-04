#include "gtest/include/gtest/gtest.h"
#include "rob/object.h"
#include "rob/variant.h"

namespace rob {

TEST(Object, property) {
  Object obj;
  obj.set_property("object_name", Variant("object 1"));
  EXPECT_EQ("object 1", obj.object_name());
}

}  // namespace rob
