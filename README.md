# staticsql

A library for working with [StaticSQL](https://github.com/iteg-hq/staticsql) entity metadata files.

## Quick start

Install using pip:

```
pip install staticsql
```

You can check which version of staticsql you have installed by importing it:

```
>>> import staticsql
>>> staticsql.__version__
'0.9.3'
```

`staticsql` can get 

- Create metadata programmatically, using `Entity` and `Attribute`
- Loading existing json files
- Parsing SQL files
- Extracting from live databases

### Using `Entity` and `Attribute`

If you have no other source for metadata definitions, you can create them in code, by using the `Entity` and `Attribute` classes:

```python
>>> from staticsql.entity import Entity, Attribute
>>> 
>>> entity = Entity(schema="dbo", name="Person")
>>>
>>> name_attribute = Attribute(name="Name", data_type="NVARCHAR(50)")
>>> age_attribute = Attribute(name="Age", data_type="INT", is_nullable=False)
>>> entity.attributes.extend([name_attribute, age_attribute])
>>> 
>>> print(entity.json())
{
    "schema": "dbo",
    "name": "Person",
    "attributes": [
        {
            "name": "Name",
            "data_type": "NVARCHAR(50)",
            "is_nullable": True
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

The `save()` method of `Entity` saves the metadata to `dbo.Person.json` - the name is constructed using the schema and entity names. You can pass a path to `save` to save it under a different name.

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

In this case, calling `save()` with no arguments saves the file to the path from which it was loaded, and passing a path to `save()` saves it somewhere else.

## Parsing SQL

If the entities you're working with exist as CREATE TABLE statements (from a data modelling tool or a legacy solution), you can turn them into metadata objects by using `staticsql.sql.parse()`:

```python
>>> import staticsql.sql
>>> 
>>> print(staticsql.sql.parse("""
... CREATE TABLE dbo.Person (
...     [Name] NVARCHAR(50) NOT NULL PRIMARY KEY
...   , Age INT NULL
... )
... """, unique_tag="unique").json())
{
    "schema": "dbo",
    "name": "Person",
    "attributes": [
        {
            "name": "Name",
            "data_type": "NVARCHAR(50)",
            "is_nullable": false,
            "tags": [
                "unique:1"
            ]
        },
        {
            "name": "Age",
            "data_type": "INT",
            "is_nullable": true
        }
    ]
}
>>>
```

Passing `unique_tag` tells `staticsql` to tag the metadata with primary key information. If you don't pass it, no tags will be added. 

You can also use `parse()` on view definitions:

```
>>> print(parse("""
... CREATE VIEW schema.Person
... AS
... SELECT 
...     'Bruce Wayne' AS [Name]
...   , 53 AS Age
... FROM schema.Table
... """).json())
{
    "schema": "schema",
    "name": "Person",
    "attributes": [
        {
            "name": "Name",
            "data_type": null,
            "is_nullable": null
        },
        {
            "name": "Age",
            "data_type": null,
            "is_nullable": null
        }
    ]
}
```

Neither data types nor nullability of the columns are inferred.

## Extracting from databases

You can extract metadata from live databases using `staticsql.database.extract()`:

```python
>>> import staticsql.database
>>> import pyodbc
>>> with pyodbc.connect("Connection=String;goes=here;") as conn:
...     for entity in staticsql.database.extract(conn):
...         entity.save()
```

This creates one file per entity and will extract all metadata for views, including column data types and nullability.

