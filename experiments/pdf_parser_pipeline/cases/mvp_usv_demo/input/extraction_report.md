# Extraction Report: usv_yusupovo_village

## Summary

- generated_at: `2026-05-20T11:44:28`
- sources: `3`
- demo_parameters_for_review: `228`
- AI: `not used`

## Sources

| source_id | source_file | pages | parsed_dir |
| --- | --- | ---: | --- |
| `kr1_foundation` | `ЮСВ КР1.pdf` | `12` | `parsed/kr1_foundation` |
| `kr2_above_zero` | `ЮСВ КР2.pdf` | `31` | `parsed/kr2_above_zero` |
| `ar_architecture` | `ЮСВ АР.pdf` | `21` | `parsed/ar_architecture` |

## Artifacts

Each parsed source keeps separate raw parser artifacts:

- `full_text.txt`
- `pages_text.json`
- `blocks.json`
- `tables.json`
- `tables.xlsx`
- `summary.json`
- `page_images/`

Merged files keep source boundaries and page references. They do not replace source-specific parsed folders.

## Notes

- `extracted_parameters_for_review.json` is a deterministic demo extraction.
- Every extracted parameter has `source_file`, `source_id`, `page`, and `section_title`.
- Parameters are marked `needs_human_review`.
