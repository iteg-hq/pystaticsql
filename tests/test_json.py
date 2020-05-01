
import unittest

from staticsql.entity import Entity, Attribute


class Test_JsonOutput(unittest.TestCase):
    def test_output(self):
        entity = Entity(schema="dbo", name="Person")
        entity.attributes.extend([
            Attribute(name="Name",
                    data_type="NVARCHAR(50)",
                    is_nullable=False),
            Attribute(name="Age",
                    data_type="INT",
                    is_nullable=False)])
        self.assertEqual(entity.json(), """{
    "schema": "dbo",
    "name": "Person",
    "attributes": [
        {
            "name": "Name",
            "data_type": "NVARCHAR(50)",
            "is_nullable": false
        },
        {
            "name": "Age",
            "data_type": "INT",
            "is_nullable": false
        }
    ]
}""")