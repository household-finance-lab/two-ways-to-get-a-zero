# Reproduction status

**As of 25 August 2026.** What in this repository has been verified to run, what
has not, and what would settle the difference.

This file exists because the lab's stated practice is to keep the receipts and
to report what was actually done. It is a statement about the *repository*, not
a retraction of any finding.

---

## Verified

**The Stata layer ran, and it checks itself.** `01_build.do` asserts its expected
values in code and halts if the reconstruction drifts: weighted mean correct of
5.33 against FINRA's published 5.3, male and female incorrect counts of 3.31 and
3.33, 64 quiz refusals, analytic sample of 2,797. The committed build log
records the gate passing. `02_analyze.do` ran against that build and its log is
committed.

**`code/audit_spec.py` reproduces the committed item audit exactly.** The module
was reconstructed on 2026-08-25 from `docs/nonquiz-dk-item-audit.csv` after the
original was lost. The reconstruction is asserted at import time: if the module
and the CSV ever disagree, the import fails. See the provenance note in the file
itself.

**All five scripts import and resolve their paths inside the repository.** No
absolute or machine-specific path remains anywhere in the codebase.

---

## Not yet verified

**The pipeline has never been run end to end from this repository.** The Stata
was run on one machine; the Python was written and executed in an assistant chat
session, against an uploaded file. The two halves have not been connected in one
pass by anyone.

**The Stata export and the Python input do not share a filename.**
`01_build.do` writes `nfcs_p1_built_analytic.csv`. As transferred, all three
Python scripts read `nfcs_p1_final_analytic.csv` — a name this repository never
produces. Something happened between the two steps that is not written down: a
rename, or a different file. The scripts now point at the Stata export directly,
which is the intended chain, but **that the two files are the same file is an
assumption, not an established fact.**

**The committed prediction tables were not produced by the committed code.** As
transferred, `03_` and `04_` wrote `nested_cv_summary.csv` and
`symmetric_cv_summary.csv` with two header rows. The committed tables are named
`prediction_nested_results.csv` and `prediction_symmetric_results.csv` and have
one. They were renamed and reshaped by hand after the scripts ran. The scripts
now emit the committed filenames and layout directly, so the mismatch will not
recur — but the *numbers* currently in those files still come from a run this
code has not been shown to reproduce.

Nothing here suggests the numbers are wrong. It means the repository does not
yet demonstrate that they are right, which is a different claim and the one this
repository exists to support.

---

## What would settle it

One clean run, from the repository root, on a machine with the FINRA data in
`data/`:

```
do code/01_build.do          # expect: VALIDATION GATE PASSED, n = 2,797
do code/02_analyze.do
python code/03_nested_prediction.py
python code/04_symmetric_comparison.py
python code/05_nonquiz_dk_sensitivity.py
```

Then compare the regenerated tables in `output/` against the committed ones.

Three outcomes:

- **They match.** Delete the "not yet verified" section above, and the
  repository's reproducibility claim is fully backed.
- **They differ in the last decimals.** Expected if scikit-learn or Stata
  versions moved. Record the versions used and note the tolerance.
- **They differ materially.** Then the input to the Python layer was not the
  Stata export, and the provenance of `nfcs_p1_final_analytic.csv` needs to be
  established before the predictive claims are published.

Until that run happens, the inferential result is supported by a logged,
self-validating build. The predictive result is supported by output whose
generating run cannot be traced from this repository.

---

## A note on how the code was written

The Python layer was drafted with AI assistance. That is not a defect and needs
no apology — it is ordinary research practice now, and the code is legible,
conventional, and open to inspection like any other.

It does carry one practical consequence worth naming: code written inside a chat
session runs in a sandbox that disappears, so the execution environment, the
input file, and any helper modules are lost unless deliberately saved. That is
exactly what happened here — `audit_spec.py` vanished, and the input filename no
longer matches anything on disk. The fix is not to write less code that way. It
is to run the final version once in the repository, from the repository, and
commit what comes out.
