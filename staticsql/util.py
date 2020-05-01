import codecs

boms = {
    "utf-8": codecs.BOM_UTF8,
    "utf-16 (big-endian)": codecs.BOM_UTF16_BE,
    "utf-16 (little-endian)": codecs.BOM_UTF16_LE,
}

def remove_boms(path):
    with open(path, 'rb') as f:
        content = f.read()
    for bom_name, bom in boms.items():
        bom_length = len(bom)
        if content[:bom_length] == bom:
            print(f"{path}: Removing {bom_name} byte-order mark")
            with open(path, 'wb') as f:
                f.write(content[bom_length:])
            break

