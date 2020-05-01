import itertools

from .entity import Entity, Attribute

extract_query = """
SELECT
    c.TABLE_SCHEMA AS schema_name
  , c.TABLE_NAME AS table_name
  , c.COLUMN_NAME AS attribute_name
  , LOWER(c.DATA_TYPE) AS type_name
  , CASE c.CHARACTER_MAXIMUM_LENGTH 
        WHEN -1 THEN 'MAX'
        ELSE CAST(CHARACTER_MAXIMUM_LENGTH AS NVARCHAR(100))
    END AS max_length
  , c.NUMERIC_PRECISION AS precision
  , c.NUMERIC_SCALE AS scale
  , CASE c.IS_NULLABLE
        WHEN 'YES' THEN 1
        WHEN 'NO' THEN 0
    END AS is_nullable
  , CASE WHEN kcu.ORDINAL_POSITION IS NULL THEN 0 ELSE 1 END AS is_primary_key
FROM INFORMATION_SCHEMA.COLUMNS AS c
LEFT JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS AS tc
  ON  tc.TABLE_CATALOG = c.TABLE_CATALOG
  AND tc.TABLE_SCHEMA = c.TABLE_SCHEMA
  AND tc.TABLE_NAME = c.TABLE_NAME
  AND tc.CONSTRAINT_TYPE = 'PRIMARY KEY'
LEFT JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE AS kcu
  ON  kcu.TABLE_CATALOG = c.TABLE_CATALOG
  AND kcu.TABLE_SCHEMA = c.TABLE_SCHEMA
  AND kcu.TABLE_NAME = c.TABLE_NAME
  AND kcu.COLUMN_NAME = c.COLUMN_NAME
"""


# Mappings af sys-schema-attributter til datatyper
type_formats = {
    "bit": "BIT",
    "int": "INT",
    "bigint": "BIGINT",
    "smallint": "SMALLINT",
    "tinyint": "TINYINT",
    "float": "FLOAT",
    "real": "REAL",
    "decimal": "DECIMAL({precision},{scale})",
    "numeric": "NUMERIC({precision},{scale})",
    "money": "MONEY",
    "date": "DATE",
    "datetime": "DATETIME",
    "datetime2": "DATETIME2({max_length})",
    "time": "TIME({precision})",
    "nvarchar": "NVARCHAR({max_length})",
    "varchar": "VARCHAR({max_length})",
    "nchar": "NCHAR({max_length})",
    "char": "CHAR({max_length})",
    "ntext": "NTEXT",
    "uniqueidentifier": "UNIQUEIDENTIFIER",
    "timestamp": "TIMESTAMP",
    "image": "IMAGE",
    "binary": "BINARY({max_length})",
    "varbinary": "VARBINARY({max_length})",
}


# Hent alle tabeller fra en database-forbindelse
def extract(conn, unique_tag="unique"):
    # conn = pyodbc.connect(connection_string, autocommit=True)
    cursor = conn.cursor()
    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED")
    cursor.execute(extract_query)
    attributes = cursor.fetchall()
    entities = list()

    for (schema_name, entity_name), entity_attributes in itertools.groupby(attributes, lambda row: row[0:2]):
        entity = Entity(schema=schema_name, name=entity_name)
        entities.append(entity)

        for _, _, attribute_name, type_name, max_length, precision, scale, is_nullable, is_primary_key in entity_attributes:
            attribute = Attribute(name=attribute_name)
            entity.attributes.append(attribute)
            attribute.data_type = type_formats[type_name].format(max_length=max_length, precision=precision, scale=scale)
            attribute.is_nullable = bool(is_nullable)
            if unique_tag and is_primary_key:
                attribute.tags.append(unique_tag)
    return entities
