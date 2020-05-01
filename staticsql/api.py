import requests

from .entity import Entity, Attribute

type_map = {
  ('array', None): "object",
  ('boolean', None): "BIT",
  ('integer', 'int32'): "INT",
  ('integer', 'int64'): "BIGINT",
  ('number', 'double'): "DOUBLE",
  ('object', None): "object",
  ('string', 'byte'): "NVARCHAR(500)", # base64 encoded binary stuff
  ('string', 'date-time'): "DATETIME",
  ('string', None): "NVARCHAR(500)",
  ('string', 'uuid'): "UNIQUEIDENTIFIER",
}

def from_swagger(url, schema=None):
    response = requests.get(url)
    doc = response.json()
    entities = list()
    if "info" in doc:
        schema = schema or doc["info"]["title"] or "dbo"

    for model_name, model in doc["components"]["schemas"].items():
        entity = Entity(schema=schema, name=model_name)
        entities.append(entity)
        for prop_name, prop in model.get("properties", {}).items():
            attribute = Attribute(name=prop_name)

            # The value of this property is defined by a referenced schema
            if "$ref" in prop:
                attribute.type_name = "object"
                continue

            attribute.is_nullable = prop.get("nullable", False)
            type_name = prop.get("type", None)
            format_name = prop.get("format", None)
            attribute.data_type = type_map[type_name, format_name]
            entity.attributes.append(attribute)
    return entities
