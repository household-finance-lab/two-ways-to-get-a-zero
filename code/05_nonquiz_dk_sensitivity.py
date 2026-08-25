"""
HFL Project 1 — measurement sensitivity of the non-quiz DK control.

PURPOSE: determine whether the conclusion about quiz DK and G43 depends on how the
auxiliary non-quiz DK propensity measure is constructed. The primary inferential
analysis is NOT altered or re-optimized.

MEASUREMENT RULE (frozen before any outcome model was run):
  A candidate item is INCLUDED iff, per the 2024 Investor Survey instrument and the
  Investor data dictionary:
    1. it is administered to every continuing respondent (verified from documented skip
       logic, not from patterns of nonmissing data);
    2. it offers code 98 = "Don't know" as a substantive response option;
    3. it is not a quiz item, not G23, not the outcome G43, not a variable used as a
       model covariate elsewhere in the study (G2, G40, G41), and not an eligibility
       screener where selecting DK terminated the interview (A1, A3);
    4. it is not an ID, weight, or demographic.
  Eligibility was determined without reference to G43 or to any outcome result.

BATTERY BALANCING (specified before running): six question blocks are administered as
grids (B2 x11, C22 x4, C23 x4, F30 x11, F31 x11, G30 x6 = 47 rows). Each remaining
eligible item is its own block (22). The balanced index is the unweighted mean across
all 28 BLOCKS of the within-block DK rate, so an 11-row grid carries the same weight
as a stand-alone question.

MODELS: survey-weighted multinomial logit of G43 (No base / Don't know / Yes) on
n_correct, n_dk, age, education, income, sex, ethnicity — identical to the primary
Stata specification. Weighted MLE with linearized (sandwich) variance; validated to
four decimals against the Stata svy: mlogit output before use.

NOTE ON READING THE DATA: the exported analytic CSV carries value LABELS. One
legitimate response label is the string "None" (B3 = "None" trades in 12 months),
which pandas converts to missing under default settings. keep_default_na=False is
required.
"""
import numpy as np, pandas as pd
from scipy import stats
from wmnl import fit_wmnl, ame
from audit_spec import SPEC
from paths import DOCS, OUTPUT, require_analytic_csv

CSV = require_analytic_csv()

audit = pd.DataFrame(SPEC)
audit.to_csv(DOCS / 'nonquiz-dk-item-audit.csv', index=False)
ELIG = [v.lower() for v in audit.loc[audit.include=='INCLUDE','variable']]

GRIDS = {'B2':['b2_1','b2_2','b2_3','b2_4','b2_5','b2_7','b2_20','b2_21','b2_23','b2_24','b2_25'],
         'C22':['c22_1','c22_2','c22_3','c22_4'],
         'C23':['c23_1','c23_2','c23_3','c23_4'],
         'F30':['f30_1','f30_2','f30_3','f30_4','f30_5','f30_6','f30_7','f30_8','f30_9','f30_10','f30_12'],
         'F31':['f31_1','f31_2','f31_3','f31_4','f31_5','f31_6','f31_7','f31_10','f31_40','f31_41','f31_42'],
         'G30':['g30_1','g30_2','g30_3','g30_4','g30_5','g30_6']}
IDX30 = ['a2','b30_2024','b3','b4_2024','b5','b33','b10','b40','b41','b23','c22_1','c22_2','c22_3',
         'c22_4','c40','c23_1','c23_2','c23_3','c23_4','c24','c26','c7','d40','d31','d41','e2','e6',
         'f40','g31','g42']

d = pd.read_csv(CSV, low_memory=False, keep_default_na=False)
d.columns = [c.strip() for c in d.columns]
d = d[d['g43_3'].isin(['No', "Don't know", 'Yes'])].copy()
for c in ['n_correct','n_dk','wgt1','nonquiz_dk_share']:
    d[c] = d[c].astype(float)

DK = lambda v: (d[v].astype(str).str.strip() == "Don't know").astype(float)

# ---- measures -----------------------------------------------------------------
d['idx30']  = sum(DK(v) for v in IDX30) / len(IDX30)
d['idx69']  = sum(DK(v) for v in ELIG)  / len(ELIG)
gridmembers = {v for g in GRIDS.values() for v in g}
blocks = [GRIDS[g] for g in GRIDS] + [[v] for v in ELIG if v not in gridmembers]
d['idx69_bal'] = sum(sum(DK(v) for v in b)/len(b) for b in blocks) / len(blocks)
types = {}
for t in audit.loc[audit.include=='INCLUDE','dk_opportunity_type'].unique():
    vs = [v.lower() for v in audit.loc[(audit.include=='INCLUDE') &
                                       (audit.dk_opportunity_type==t),'variable']]
    key = 'type_' + t.split('/')[0].replace(' ','_')
    types[key] = vs
    d[key] = sum(DK(v) for v in vs) / len(vs)

assert np.allclose(d['idx30'], d['nonquiz_dk_share'], atol=1e-9), "idx30 must match the stored 30-item measure"
print(f"n = {len(d)}   blocks for balancing = {len(blocks)}   eligible items = {len(ELIG)}")

MEASURES = [('idx30','30-item (as previously analyzed)',len(IDX30)),
            ('idx69','rule-derived, item-weighted',len(ELIG)),
            ('idx69_bal','rule-derived, battery-balanced',len(ELIG))] + \
           [(k,f'sub-index: {k.replace("type_","")}',len(v)) for k,v in types.items()]

print("\n=== Descriptives of each non-quiz DK measure ===")
print(f"{'measure':<28}{'items':>6}{'mean':>9}{'SD':>8}{'min':>7}{'max':>7}{'r with n_dk':>13}")
for k, lab, ni in MEASURES:
    r = np.corrcoef(d[k], d['n_dk'])[0,1]
    print(f"{lab:<28}{ni:>6}{d[k].mean():>9.4f}{d[k].std():>8.4f}{d[k].min():>7.3f}{d[k].max():>7.3f}{r:>13.3f}")

print("\n=== Correlations among the alternative measures ===")
print(d[[m[0] for m in MEASURES]].corr().round(3).to_string())

# ---- models -------------------------------------------------------------------
y = d['g43_3'].map({'No':0,"Don't know":1,'Yes':2}).values
w = d['wgt1'].values

def design(extra=None):
    parts=[np.ones((len(d),1)), d[['n_correct','n_dk']].values]; names=['_cons','n_correct','n_dk']
    if extra: parts.append(d[[extra]].values); names.append(extra)
    for var, base in [('agecat','18-34'),('educ','Some college or less'),
                      ('income','<$50K'),('sex','Male'),('ethnicity','White non-Hispanic')]:
        for c in [c for c in sorted(d[var].unique()) if c != base]:
            parts.append((d[var]==c).values.astype(float).reshape(-1,1)); names.append(f'{var}={c}')
    return np.hstack(parts), names

def run(extra, label):
    X, nm = design(extra)
    f = fit_wmnl(X, y, w, [0,1,2])
    out = dict(label=label)
    for k, tag in [(2,'yes'), (1,'dk')]:
        e, s = ame(f, nm.index('n_dk'), k)
        out[f'ndk_{tag}'] = e; out[f'ndk_{tag}_se'] = s
        out[f'ndk_{tag}_lo'] = e-1.96*s; out[f'ndk_{tag}_hi'] = e+1.96*s
        out[f'ndk_{tag}_p'] = 2*(1-stats.norm.cdf(abs(e/s)))
        if extra:
            e2, s2 = ame(f, nm.index(extra), k)
            out[f'idx_{tag}'] = e2; out[f'idx_{tag}_se'] = s2
            out[f'idx_{tag}_p'] = 2*(1-stats.norm.cdf(abs(e2/s2)))
    return out

res = [run(None, 'No non-quiz control (primary)')] + [run(k, lab) for k, lab, _ in MEASURES]
base = res[0]

print("\n=== AME of quiz n_dk on P(G43 = Yes) ===")
print(f"{'specification':<34}{'AME':>9}{'SE':>8}{'95% CI':>20}{'p':>9}{'vs base':>10}")
for r in res:
    print(f"{r['label']:<34}{r['ndk_yes']:>9.4f}{r['ndk_yes_se']:>8.4f}"
          f"  [{r['ndk_yes_lo']:+.4f},{r['ndk_yes_hi']:+.4f}]{r['ndk_yes_p']:>9.3f}"
          f"{r['ndk_yes']-base['ndk_yes']:>+10.4f}")

print("\n=== AME of quiz n_dk on P(G43 = Don't know) ===")
print(f"{'specification':<34}{'AME':>9}{'SE':>8}{'95% CI':>20}{'p':>9}{'vs base':>10}")
for r in res:
    print(f"{r['label']:<34}{r['ndk_dk']:>9.4f}{r['ndk_dk_se']:>8.4f}"
          f"  [{r['ndk_dk_lo']:+.4f},{r['ndk_dk_hi']:+.4f}]{r['ndk_dk_p']:>9.3f}"
          f"{r['ndk_dk']-base['ndk_dk']:>+10.4f}")

print("\n=== AME of the non-quiz measure itself (per 1.0 = all items DK) ===")
print(f"{'specification':<34}{'on P(Yes)':>12}{'p':>8}{'on P(DK)':>12}{'p':>8}")
for r in res[1:]:
    print(f"{r['label']:<34}{r['idx_yes']:>12.4f}{r['idx_yes_p']:>8.3f}"
          f"{r['idx_dk']:>12.4f}{r['idx_dk_p']:>8.3f}")

pd.DataFrame(res).to_csv(OUTPUT / 'nonquiz_dk_sensitivity_results.csv', index=False)
print("\nWritten: nonquiz-dk-item-audit.csv, nonquiz_dk_sensitivity_results.csv")
