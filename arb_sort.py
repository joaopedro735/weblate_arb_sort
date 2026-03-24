"""
Weblate addon: Sort Flutter ARB keys alphabetically.

ARB files use `@key` entries as metadata for the corresponding `key`.
This addon sorts all keys alphabetically and ensures each `@key` metadata
entry immediately follows its parent `key`.

Special keys (e.g. `@@locale`) that start with `@@` are kept at the top.
"""

import json
from weblate.addons.base import BaseAddon
from weblate.addons.events import AddonEvent


def sort_arb_content(content: str) -> str:
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
    data = json.loads(content)

    # Separate @@-keys (locale metadata), regular keys, and @-metadata keys.
    locale_keys = {k: v for k, v in data.items() if k.startswith("@@")}
    meta_keys = {k: v for k, v in data.items() if k.startswith("@") and not k.startswith("@@")}
    regular_keys = {k: v for k, v in data.items() if not k.startswith("@")}

    # Sort regular keys alphabetically (case-insensitive).
    sorted_regular = sorted(regular_keys.keys(), key=str.casefold)

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

    return json.dumps(sorted_data, ensure_ascii=False, indent=2) + "\n"


class ArbSortAddon(BaseAddon):
    """Weblate addon that sorts Flutter ARB file keys alphabetically."""

    events = (AddonEvent.EVENT_PRE_COMMIT,)
    name = "weblate_arb_sort.arb_sort.ArbSortAddon"
    verbose = "Sort Flutter ARB keys alphabetically"
    description = (
        "Sorts all keys in Flutter ARB files alphabetically. "
        "Each @metadata key is placed immediately after its parent key. "
        "@@locale and other @@-prefixed keys are kept at the top."
    )

    @classmethod
    def can_install(cls, *, component=None, project=None, **kwargs):
        """Only allow installation on Flutter ARB file format components."""
        return component is not None and component.file_format == "arb"

    def pre_commit(self, translation, author, store_hash, activity_log_id=None, **kwargs):
        filename = translation.get_filename()
        try:
            with open(filename, "r", encoding="utf-8") as fh:
                original = fh.read()
        except FileNotFoundError:
            return

        try:
            sorted_content = sort_arb_content(original)
        except (json.JSONDecodeError, ValueError):
            # Do not corrupt the file if it is not valid JSON.
            return

        if sorted_content != original:
            with open(filename, "w", encoding="utf-8") as fh:
                fh.write(sorted_content)
