import json


class AnyType(str):
    """A special class that is always equal in not equal comparisons. Credit to pythongosssss"""

    def __ne__(self, __value: object) -> bool:
        return False


# Create the any_type instance
any_type = AnyType("*")


def get_dict_value(data: dict, dict_key: str, default=None):
    """Gets a deeply nested value given a dot-delimited key."""
    keys = dict_key.split('.')
    key = keys.pop(0) if len(keys) > 0 else None
    found = data[key] if key in data else None
    if found is not None and len(keys) > 0:
        return get_dict_value(found, '.'.join(keys), default)
    return found if found is not None else default


class PipemindDisplayAny:
    """Display any data node."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "source": (any_type, {}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    RETURN_TYPES = ()
    FUNCTION = "main"
    OUTPUT_NODE = True
    CATEGORY = "Pipemind"

    def main(self, source=None, unique_id=None, extra_pnginfo=None):
        value = 'None'
        if isinstance(source, str):
            value = source
        elif isinstance(source, (int, float, bool)):
            value = str(source)
        elif source is not None:
            try:
                value = json.dumps(source)
            except Exception:
                try:
                    value = str(source)
                except Exception:
                    value = 'source exists, but could not be serialized.'

        # Save the output to the pnginfo so it's pre-filled when loading the data.
        if extra_pnginfo and unique_id:
            for node in get_dict_value(extra_pnginfo, 'workflow.nodes', []):
                if str(node['id']) == str(unique_id):
                    node['widgets_values'] = [value]
                    break

        return {"ui": {"text": (value,)}}

