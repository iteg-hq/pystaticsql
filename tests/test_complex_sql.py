import unittest

import staticsql.sql

simple_ddl = """
CREATE TABLE my_schema.MyTable (
    i INT NOT NULL IDENTITY(1,1)
)
"""

class Test_SqlParser(unittest.TestCase):
    def setUp(self):
        self.entity = staticsql.sql.parse(simple_ddl)

    def test_schema(self):
        self.assertEqual(self.entity.schema, "my_schema")

    def test_name(self):
        self.assertEqual(self.entity.name, "MyTable")

    def test_attribute(self):
        self.assertEqual(len(self.entity.attributes), 1)
        self.assertEqual(self.entity.attributes[0].name, "i")


