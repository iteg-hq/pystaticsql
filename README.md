# staticsql

`staticsql` is a library for working with StaticSQL entity metadata files. For more information about StaticSQL, see https://github.com/iteg-hq/staticsql.

## Quick start

Install:

```
pip install staticsql
```

Version check:

```
>>> import staticsql
>>> staticsql.__version__
'0.9.3'
```

`staticsql` provides a number of ways of creating metadata objects:

- Creating them programmatically
- Loading them from existing json files
- Parsing SQL files
- Extracting them from live databases

We'll look at these in turn below.

### Using `Entity` and `Attribute`

You can create metadata definitions in code, by using the `Entity` and `Attribute` classes:

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

### Loading from json files

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

### Parsing SQL

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

### Extracting from databases

You can extract metadata from database connections using `staticsql.database.extract()`:

```python
>>> import staticsql.database
>>> import pyodbc
>>> with pyodbc.connect("Connection=String;goes=here;") as conn:
...     for entity in staticsql.database.extract(conn):
...         entity.save()
```

This creates one file per entity and will extract all metadata for views, including column data types and nullability.



