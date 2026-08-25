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

**The Python layer read the Stata build output.** As transferred, all three
Python scripts read `nfcs_p1_final_analytic.csv`, a filename this repository
never produces — `01_build.do` exports `nfcs_p1_built_analytic.csv`. Lena
confirmed on 2026-08-25 that she renamed the Stata export by hand before
uploading it. The two names refer to the same file, so the chain from build to
prediction is intact. The scripts now read the Stata export directly and the
rename step is gone.

This rests on Lena's account rather than on a file comparison. A byte-level
check happens automatically the first time the pipeline is run end to end.

---

## Not yet verified

**The pipeline has never been run end to end from this repository.** The Stata
was run on one machine; the Python was written and executed in an assistant chat
session, against the Stata export uploaded under a different name. The two
halves have not been connected in one pass by anyone.

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
- **They differ in the last decimals.** The likely outcome if scikit-learn moved
  between the original run and the rerun. Record the versions used and note the
  tolerance rather than overwriting the tables silently.
- **They differ materially.** Unexpected now that the input file is accounted
  for. Investigate before publishing the predictive claims rather than
  reconciling the tables to the new numbers.

Until that run happens, the inferential result is supported by a logged,
self-validating build. The predictive result rests on output that this code has
not yet been shown to regenerate — a narrower gap than it looks, since the input
is accounted for, but not yet closed.

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
