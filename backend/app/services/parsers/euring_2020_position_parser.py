"""
EURING 2020 Position Parser
============================
Parses a EURING 2020 string into field_name -> value using the field
order (`position`) and names defined in euring_2020.json (loaded via
the SKOS manager), which is the single source of truth for this
version's field metadata -- verified field-by-field against the
official EURING Exchange Code 2020 v202 PDF on 2026-07-22.

IMPORTANT -- how this differs from a naive "fixed width" reading of
euring_2020.json:

  As of EURING 2020, strings use '|' as a field separator (confirmed
  by D. Licheri, 2026-07-23). This parser therefore splits the input
  on '|' and maps segments to fields IN POSITION ORDER. It does NOT
  do fixed-width byte-offset slicing. The `length` attribute on each
  FieldDefinition is a maximum value length used for validation, not
  a byte offset -- summing it across fields does not give a
  meaningful "total string length" for this format.

  This module intentionally does not reuse
  `euring_2000_epe_compatible_parser.py` (a different, hardcoded,
  fixed-width-no-separator layout inherited from the legacy EPE tool)
  nor `euring_2020_official_parser.py` (an incomplete, 15-field
  prototype). Both were found during this investigation to disagree
  with euring_2020.json and with each other; using either as the
  basis for archiving would silently produce wrong facet data.

KNOWN OPEN QUESTION (not yet verified against a real production
string -- flagged in design_archivio_faccette.md): whether the
trailing, "between-scheme recovery processing only" fields (place
name, remarks, reference, current place code, more other marks --
positions 58-64 per the EURING standard, not normally stored in the
EDB) are always present as an empty segment between two pipes, or can
be omitted entirely, shortening the segment count below 64. This
parser currently REQUIRES exactly as many segments as there are
fields in euring_2020.json (64 at time of writing) and reports a
non-clean parse otherwise. Loosen this once confirmed with a real
string.
"""
from typing import Any, Dict, List

from ...models.euring_models import EuringVersion, FieldDefinition


class Euring2020PositionParser:
    """
    Parses EURING 2020 pipe-delimited strings using the position/name
    metadata from euring_2020.json (via a loaded EuringVersion model),
    instead of a second, independently-maintained field layout.
    """

    def __init__(self, version_model: EuringVersion):
        if version_model.id != "euring_2020":
            raise ValueError(
                f"Euring2020PositionParser requires the euring_2020 version model, "
                f"got '{version_model.id}'"
            )
        self.version_model = version_model
        self.separator = version_model.format_specification.field_separator or "|"
        self.fields_by_position: List[FieldDefinition] = sorted(
            version_model.field_definitions, key=lambda f: f.position
        )
        self.expected_field_count = len(self.fields_by_position)

    def parse(self, euring_string: str) -> Dict[str, Any]:
        """
        Parse a pipe-delimited EURING 2020 string.

        Returns:
            {
                "fields": {field_name: value, ...},   # canonical euring_2020.json names
                "field_count": int,                    # segments actually found
                "expected_field_count": int,            # fields defined in euring_2020.json
                "is_clean": bool,                       # True only if segment count matches exactly
                "errors": [str, ...],                   # empty if is_clean
            }

        `is_clean` is meant to be used directly by the archiving logic:
        per project decision, a string that does not parse cleanly must
        NOT be written to the canonical faceted archive (it can still be
        logged as-is in user_queries, as happens today).
        """
        errors: List[str] = []
        euring_string = (euring_string or "").strip()

        if not euring_string:
            return {
                "fields": {},
                "field_count": 0,
                "expected_field_count": self.expected_field_count,
                "is_clean": False,
                "errors": ["empty string"],
            }

        segments = euring_string.split(self.separator)

        if len(segments) != self.expected_field_count:
            errors.append(
                f"Segment count ({len(segments)}) does not match the number of fields "
                f"defined in euring_2020.json ({self.expected_field_count})"
            )

        # Map defensively up to the shorter of the two lengths so a mismatch
        # doesn't raise -- the mismatch itself is already recorded above and
        # will make is_clean False, which is what callers should act on.
        fields: Dict[str, Any] = {}
        for field_def, value in zip(self.fields_by_position, segments):
            fields[field_def.name] = value

        return {
            "fields": fields,
            "field_count": len(segments),
            "expected_field_count": self.expected_field_count,
            "is_clean": len(errors) == 0,
            "errors": errors,
        }

    def to_dict(self, euring_string: str) -> Dict[str, Any]:
        """Kept for naming parity with the other version parsers (parse/to_dict convention)."""
        return self.parse(euring_string)
