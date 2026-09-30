# Local Development Guardrails

Read this file before changing the full-estimate pipeline.

These rules were explicitly confirmed by the user on 30.09.2026 and override older notes
that suggest deploying intermediate work or preserving an old data shape merely because an
already calculated project used it.

## 1. Production And Server Are Frozen

- The deployed production bot is working and must not be changed during development of the
  complete building-shell cost basis.
- Do not connect to the production server, inspect or edit its files, restart services, upload
  archives, pull branches, replace environment files or run deployment checks unless the user
  explicitly starts a separate deployment task in the future.
- Do not build or publish a production package as a side effect of ordinary development.
- All implementation, parsing, workbook generation and regression testing happen locally on
  this Mac until the complete building shell is finished and verified.
- A successful local section is not permission to deploy that section separately.

## 2. Current Product Boundary

- The active scope is the right-hand grey cost-basis part of the estimate.
- Finish every planned building-shell section and test the complete cost-basis workflow on all
  available projects before starting the client side.
- Client columns `A:I`, client margin allocation and client print output remain a later phase.

## 3. Projects Are Tests, Not Architecture

- Previously calculated projects do not define the production schema or calculator structure.
- Do not preserve obsolete scalar fields, JSON layouts, workbook row positions or calculator
  quirks solely to keep old artifacts byte-identical.
- Build one universal typed structure from construction meaning, source evidence and confirmed
  business rules.
- Reparse source PDFs and rebuild Google-review workbooks and cost estimates with the new
  structure for USV, ARK, TRC and every other available project.
- Project names and measured project quantities belong only in fixtures, expected results and
  analytical reports. They must not appear in production branches or defaults.
- Old estimates are comparison evidence. Explain differences, fix confirmed source or estimate
  errors, and never tune universal code to reproduce an unexplained historical total.

## 4. Parser And Review Workflow

- Keep the existing parser engine, but extend its schema, targets and prompt when the approved
  universal contract requires new structured fields.
- Information mentioned only in prose notes is not considered delivered to the calculator.
- The completed local workflow must remain:
  `PDF -> structured extraction -> intermediate Google review -> confirmed canonical input ->`
  `cost-basis calculator -> final Excel cost basis`.
- Do not edit the extraction prompt ahead of an agreed typed contract and tests.

## 5. Git And GitHub Are Not Deployment

- Make small, reviewable commits during research and implementation and push them to GitHub for
  history and backup.
- Work on a feature branch. A commit or push does not authorize a server update.
- This repository currently has no `.github/workflows` automation, so an ordinary push does not
  run deployment from this repository. Still never assume that Git history itself is a release.
- Do not run scripts under `deploy/`, create/upload a production archive, use SSH/SCP/rsync, pull
  on the server or run `systemctl` as part of local feature work.
- Later deployment is a separate decision: select the approved commits/version, build the
  minimal production package from the manifest, review it, and only then deploy under a new
  explicit user instruction.
- Never commit secrets, tokens, proxy credentials, local environment files, generated job data
  or unrelated user files. Stage only files belonging to the current logical change.

## 6. Completion Gate

Server work remains prohibited until all of the following are true:

1. all planned building-shell cost-basis sections are implemented;
2. parser, review workbook, calculators and final cost-basis Excel work together locally;
3. all available projects have been reparsed and recalculated with the universal structures;
4. discrepancies are resolved or explicitly recorded for review;
5. the user explicitly approves a separate production deployment phase.
