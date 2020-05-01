import os
import json
import collections

def load(path):
    path = os.path.abspath(path)

    with open(path, 'rb') as f:
        json_doc = json.load(f, object_pairs_hook=collections.OrderedDict)

    entity = Entity(
        schema = json_doc.get("schema"),
        name = json_doc.get("name"),
        tags = json_doc.get("tags", []),
        )

    for json_attribute in json_doc.get("attributes", []):
        entity.attributes.append(Attribute(
            name=json_attribute.get("name"),
            data_type=json_attribute.get("data_type"),
            is_nullable=json_attribute.get("is_nullable"),
            tags=list(json_attribute.get("tags",[])),
        ))
    entity.path = path
    return entity


class Entity(object):
    def __init__(self, schema=None, name=None, tags=[], attributes=[]):
        self.schema = schema
        self.name = name
        self.tags = list(tags)
        self.attributes = list()
        self.path = None

    def get_tag(self, tag):
        for my_tag in self.tags:
            if my_tag == tag:
                return True
            if my_tag.startswith(tag + ":"):
                return my_tag[len(tag)+1:]
        else:
            return False

    def __repr__(self):
        return f"<Entity {self.schema or ...}.{self.name or ...}>"

    def get_attribute(self, name):
        for attr in self.attributes:
            if attr.name == name:
                return attr
        else:
            raise KeyError(name)

    def copy(self):
        return Entity(      
            schema = self.schema,
            name = self.name,
            attributes = [attr.copy() for attr in self.attributes],
            tags = list(self.tags),
        )

    def save(self, path=None):
        self.path = path or self.path
        with open(self.path or f"{self.schema}.{self.name}.json", 'w') as f:
            f.write(self.json())

    def json(self):
        # Create a clean version of the object
        json_doc = collections.OrderedDict({
            "schema": self.schema,
            "name": self.name,
            "tags": list(self.tags),
            "attributes": list(),
        })

        if not json_doc["tags"]:
            del json_doc["tags"]

        for attr in self.attributes:
            json_attribute = collections.OrderedDict({
                "name": attr.name,
                "data_type": attr.data_type,
                "is_nullable": attr.is_nullable,
                "tags": list(attr.tags)
            })

            if not json_attribute["tags"]:
                del json_attribute["tags"]

            json_doc["attributes"].append(json_attribute)
        return json.dumps(json_doc, indent=4)

    def sql(self, unique_tag=None):
        pass


class Attribute(object):
    def __init__(self, name=None, data_type=None, is_nullable=None, tags=list()):
        self.name = str(name)
        self.data_type = str(data_type)
        self.is_nullable = bool(is_nullable)
        self.tags = list(tags)

    def __repr__(self):
        return f"<Attribute {self.name or ...}>"

    def copy(self):
        return Attribute(
            name=self.name,
            data_type=self.data_type,
            is_nullable=self.is_nullable,
            tags=list(self.tags),
        )

    def get_tag(self, tag):
        for my_tag in self.tags:
            if my_tag == tag:
                return True
            if my_tag.startswith(tag + ":"):
                return my_tag[len(tag)+1:]
        else:
            return False