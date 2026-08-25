"""Repository-relative paths for the Project 1 Python layer.

Every script imports from here so that no absolute, machine-specific path
appears anywhere in the codebase. Paths resolve from this file's own location,
so the scripts run correctly regardless of the working directory:

    python code/03_nested_prediction.py
    cd code && python 03_nested_prediction.py

both work.

The analytic CSV is produced by ``code/01_build.do`` (see the export at the end
of Block B) and is not redistributed here; the NFCS belongs to the FINRA
Investor Education Foundation. See ``data/README.md``.
"""
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

CODE = REPO / "code"
DATA_DIR = REPO / "data"
DOCS = REPO / "docs"
OUTPUT = REPO / "output"
TABLES = OUTPUT / "tables"
LOGS = REPO / "logs"

# Written by 01_build.do as "$OUT/nfcs_p1_built_analytic.csv".
ANALYTIC_CSV = OUTPUT / "nfcs_p1_built_analytic.csv"

for _d in (OUTPUT, TABLES, LOGS):
    _d.mkdir(parents=True, exist_ok=True)


def require_analytic_csv() -> Path:
    """Return the analytic CSV path, failing with a useful message if absent."""
    if not ANALYTIC_CSV.exists():
        raise SystemExit(
            f"Analytic dataset not found at {ANALYTIC_CSV}.\n"
            "Run the Stata build first, from the repository root:\n"
            "    do code/01_build.do\n"
            "See data/README.md for how to obtain the source NFCS files."
        )
    return ANALYTIC_CSV
