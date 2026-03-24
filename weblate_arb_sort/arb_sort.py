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

from weblate_arb_sort._sort import sort_arb_content


class ArbSortAddon(BaseAddon):
    """Weblate addon that sorts Flutter ARB file keys alphabetically."""

    events = {AddonEvent.EVENT_PRE_COMMIT}
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

        indent = getattr(translation.store, "json_indent", None)
        try:
            sorted_content = sort_arb_content(original, indent=indent)
        except (json.JSONDecodeError, ValueError):
            # Do not corrupt the file if it is not valid JSON.
            return

        if sorted_content != original:
            with open(filename, "w", encoding="utf-8") as fh:
                fh.write(sorted_content)
