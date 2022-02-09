
async def json_object_prettify(objecc):
    dicc = objecc.__dict__
    return "".join(
        f"**{key}:** `{value}`\n"
        for key, value in dicc.items()
        if key not in ["pinned_message", "photo", "_", "_client"]
    )


async def json_prettify(data):
    output = ""
    try:
        for key, value in data.items():
            output += f"**{str(key).capitalize()}:** `{value}`\n"
    except Exception:
        for datas in data:
            for key, value in datas.items():
                output += f"**{str(key).capitalize()}:** `{value}`\n"
            output += "------------------------\n"
    return output
