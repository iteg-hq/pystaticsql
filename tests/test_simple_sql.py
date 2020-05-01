import unittest

import staticsql.sql


class Test_SqlParser(unittest.TestCase):

    def test_no_name(self):
        with self.assertRaises(staticsql.sql.ParseException):
            staticsql.sql.parse("CREATE TABLE (i INT)")


    def test_no_schema(self):
        entity = staticsql.sql.parse("CREATE TABLE MyTable (i INT)")
        self.assertEqual(entity.schema, None)
        self.assertEqual(entity.name, "MyTable")

    def test_schema(self):
        entity = staticsql.sql.parse("CREATE TABLE schema.MyTable (i INT)")
        self.assertEqual(entity.schema, "schema")
        self.assertEqual(entity.name, "MyTable")

    def test_schema_whitespace(self):
        entity = staticsql.sql.parse("CREATE TABLE schema  .MyTable (i INT)")
        self.assertEqual(entity.schema, "schema")
        self.assertEqual(entity.name, "MyTable")

    def test_postname_junk(self):
        entity = staticsql.sql.parse("CREATE TABLE schema.MyTable THIS IS ASC 1234 . JUNK (i INT)")
        self.assertEqual(entity.schema, "schema")
        self.assertEqual(entity.name, "MyTable")

    def test_no_table_definition(self):
        with self.assertRaises(staticsql.sql.ParseException):
            staticsql.sql.parse("CREATE TABLE schema.MyTable")

    def test_unclosed_definition(self):
        with self.assertRaises(staticsql.sql.ParseException):
            staticsql.sql.parse("CREATE TABLE schema.MyTable ( i int")


    def test_attribute_name(self):
        entity = staticsql.sql.parse("CREATE TABLE schema.MyTable (i INT)")
        self.assertEqual(entity.attributes[0].name, "i")

    # Single attribute
    def test_attribute_data_type(self):
        entity = staticsql.sql.parse("CREATE TABLE schema.MyTable (i INT)")
        self.assertEqual(entity.attributes[0].data_type, "INT")

    # Data type
    def test_attribute_data_type_casing(self):
        entity = staticsql.sql.parse("CREATE TABLE schema.MyTable (i int)")
        self.assertEqual(entity.attributes[0].data_type, "INT")

    def test_attribute_data_type_no_params(self):
        with self.assertRaises(staticsql.sql.ParseException):
            staticsql.sql.parse("CREATE TABLE schema.MyTable (i INT())")

    def test_attribute_data_bad_param(self):
        with self.assertRaises(staticsql.sql.ParseException):
            staticsql.sql.parse("CREATE TABLE schema.MyTable (i NVARCHAR(FOO))")

    def test_attribute_data_type_max(self):
        entity = staticsql.sql.parse("CREATE TABLE schema.MyTable (i NVARCHAR(MAX))")
        self.assertEqual(entity.attributes[0].data_type, "NVARCHAR(MAX)")

    def test_attribute_data_type_single_param(self):
        entity = staticsql.sql.parse("CREATE TABLE schema.MyTable (i NVARCHAR(42))")
        self.assertEqual(entity.attributes[0].data_type, "NVARCHAR(42)")

    def test_attribute_data_type_double_param(self):
        entity = staticsql.sql.parse("CREATE TABLE schema.MyTable (i DECIMAL(18, 4))")
        self.assertEqual(entity.attributes[0].data_type, "DECIMAL(18, 4)")

    def test_attribute_implicit_nullability(self):
        entity = staticsql.sql.parse("CREATE TABLE schema.MyTable (i INT)")
        self.assertTrue(entity.attributes[0].is_nullable)

    def test_attribute_explicit_nullability(self):
        entity = staticsql.sql.parse("CREATE TABLE schema.MyTable (i INT NULL)")
        self.assertTrue(entity.attributes[0].is_nullable)

    def test_attribute_explicit_nonnullability(self):
        entity = staticsql.sql.parse("CREATE TABLE schema.MyTable (i INT NOT NULL)")
        self.assertFalse(entity.attributes[0].is_nullable)

