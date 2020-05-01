# StaticSQL

A library for working with [StaticSQL](https://github.com/iteg-hq/staticsql) entity metadata files.

## Quick start

Install using pip:

```
pip install staticsql
```

You can create metadata from scratch:

```python
>>> from staticsql.entity import Entity, Attribute
>>> 
>>> entity = Entity(schema="dbo", name="Person")
>>> 
>>> entity.attributes.extend(
...     Attribute(name="Name",
...               data_type="NVARCHAR(50)",
...               is_nullable=False),
...     Attribute(name="Age",
...               data_type="INT",
...               is_nullable=False))
>>> 
>>> print(entity.json())
{
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
}
>>> entity.save()
```

The `save()` method saves the file to `"dbo.Person.json"` (the name is constructed using the schema and table names). Pass a path to `save` to save it somewhere else.

You can load, modify and save existing metadata files:

```python
>>> import staticsql.entity
>>> 
>>> entity = staticsql.entity.load("dbo.Person.json")
>>> entity.attributes.append(
...     Attribute(name="Address",
...               data_type="NVARCHAR(200)",
...               is_nullable=True))
>>> entity.save()
```

In this case, the call to `save()` with no arguments saves the file to the path from which it was loaded.

You can parse `CREATE TABLE` statements using `staticsql.sql.parse()`:

```python
>>> import staticsql.sql
>>> 
>>> entity = staticsql.sql.parse("""
... CREATE TABLE dbo.Person (
...     Name NVARCHAR(50) NOT NULL PRIMARY KEY
...   , Age INT NULL
... )
... """, unique_tag="unique")
>>>
>>> print(entity.json())
... {
...     "schema": "dbo",
...     "name": "Person",
...     "attributes": [
...         {
...             "name": "Name",
...             "data_type": "NVARCHAR(50)",
...             "is_nullable": false,
...             "tags": [
...                 "unique:1"
...             ]
...         },
...         {
...             "name": "Age",
...             "data_type": "INT",
...             "is_nullable": true
...         }
...     ]
... }
```

Passing `unique_tag` tells `staticsql` to tag the metadata with primary key information.

You can extract metadata from live databases using `staticsql.database`:

```python
>>> import staticsql.database
>>> import pyodbc
>>> with pyodbc.connect(conn_str) as conn:
...     for entity in staticsql.database.extract(conn):
...         entity.save()
```

