import json


def detect_indent(content: str) -> int:
    """Return the number of spaces used for indentation in a JSON string.

    Scans lines for leading whitespace, skipping brace-only lines that are
    typically not indented at the key level. Falls back to 2 if none found.
    """
    for line in content.splitlines():
        stripped = line.lstrip(" ")
        leading = len(line) - len(stripped)
        if leading > 0 and stripped and not stripped.startswith("{") and not stripped.startswith("}"):
            return leading
    return 2


def sort_arb_content(content: str, indent: int | None = None) -> str:
    """
    Parse an ARB JSON string, sort its keys, and return the sorted JSON string.

    Sorting rules:
    - `@@`-prefixed keys (e.g. `@@locale`) are kept at the top, in their
      original relative order.
    - All other keys are sorted case-insensitively.
    - Each `@key` metadata entry is placed immediately after its parent `key`.
      If the parent key does not exist (orphaned metadata), the `@key` entry
      is sorted as if it were its parent (i.e. placed where `key` would be).
    """
    if indent is None:
        indent = detect_indent(content)
    data = json.loads(content)

    # Partition keys into three groups:
    #   locale_keys  — @@-prefixed globals like @@locale (kept at top, original order)
    #   meta_keys    — @key metadata entries (paired with their parent key)
    #   regular_keys — translatable string keys
    locale_keys = {k: v for k, v in data.items() if k.startswith("@@")}
    meta_keys = {k: v for k, v in data.items() if k.startswith("@") and not k.startswith("@@")}
    regular_keys = {k: v for k, v in data.items() if not k.startswith("@")}

    # Sort regular keys alphabetically (case-insensitive).
    sorted_regular = sorted(
        regular_keys.keys(),
        key=lambda s: (s.casefold(), s.swapcase())  # lowercase-first on ties
    )

    sorted_data = {}

    # 1. @@locale and other @@-keys first.
    for k in locale_keys:
        sorted_data[k] = locale_keys[k]

    # 2. Regular keys in alphabetical order, each followed by its @metadata.
    for key in sorted_regular:
        sorted_data[key] = regular_keys[key]
        meta_key = f"@{key}"
        if meta_key in meta_keys:
            sorted_data[meta_key] = meta_keys[meta_key]

    # 3. Orphaned @-metadata keys (no matching regular key) sorted by their
    #    effective name (the part after `@`).
    orphaned = {k: v for k, v in meta_keys.items() if k[1:] not in regular_keys}
    for k in sorted(orphaned.keys(), key=lambda x: x[1:].casefold()):
        sorted_data[k] = orphaned[k]

    return json.dumps(sorted_data, ensure_ascii=False, indent=indent) + "\n"
