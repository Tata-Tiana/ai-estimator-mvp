# Schiedel channels — no channel items at all (real project has none in the final smeta)

Added 2026-07-26. Restores the `template_case_dir` slot used by `calculation_runner/runner_registry.py`
for the USV end-to-end demo pipeline (the old `test_schiedel_vent_channels_usv` case, built on
fabricated 24/8 numbers, was deleted as part of the calculator rewrite — see
`test_schiedel_vent_channels_trc/notes.md` for the full redesign writeup).

This time grounded in the REAL delivered USV smeta directly: the "ВЕНТИЛЯЦИОННЫЕ КАНАЛЫ Schiedel"
section there has only two rows — "Кладка вентканалов Schiedel" (15,82 мп) and "Доставка вентканалов"
(1 маш) — no material/module line for this project at all in the final costing. `schiedel_channel_items`
is simply omitted here to match.

Confirms the dynamic design degrades correctly when a project genuinely has no channel material line:
no `schiedel_vent_channel_*` estimate lines appear, no error, masonry work and delivery still price
normally. Same behavior already sanity-checked ad hoc while building the redesign; this case makes it a
permanent regression test and keeps the `calculation_runner` demo pipeline's template reference valid.
