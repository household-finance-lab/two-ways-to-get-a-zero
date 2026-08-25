# Codebook

Every variable this study uses, where it came from, and how the derived measures are built. This is not the full survey documentation — FINRA's questionnaires and data dictionaries cover that, and `data/README.md` says where to get them. This covers what we actually used, so the measure can be rebuilt in any software.

## Source files

| File | Rows | Role |
|---|---|---|
| 2024 NFCS Investor Survey | 2,861 | Quiz items, outcome, self-assessed knowledge, weight |
| 2024 NFCS State-by-State | 25,539 | Demographics (merged in) |

Merge key: `NFCSID`, 1:1. All 2,861 investor records match. The Investor respondents are a subset of the State-by-State respondents — the same people, screened on `B14A_1` (owns securities outside retirement accounts) with primary or shared investment decision-making responsibility.

**Name collisions.** The two files reuse six variable names for entirely different questions: `G23` (debt attitude in State-by-State, the call-option quiz item in the Investor Survey) and `G30_1`–`G30_5` (student-loan checkboxes vs. reasons for investing). Our build script suffixes *every* State-by-State variable with `_sbs` before merging, which also catches collisions nobody has noticed.

**Missing codes.** Throughout both surveys: `98` = don't know, `99` = prefer not to say.

---

## The 11-item investment knowledge battery

Frozen at 11 items. FINRA's 2024 report states the quiz is 11 items including the new inflation question (G44), and that the call-option item (G23) is a bonus explicitly **not** counted in the 11. We exclude it.

| Variable | Item, in brief | Options | Correct code | Correct answer |
|---|---|---|---|---|
| `G4` | If you buy a company's stock… | 4 | 1 | You own part of the company |
| `G5` | If you buy a company's bond… | 4 | 2 | You have lent money to the company |
| `G6` | On bankruptcy, which security is most at risk | 3 | 2 | The company's common stock |
| `G7` | Riskier investments tend to provide higher returns over time | 2 | 1 | True |
| `G21` | Past performance is a good indicator of future results | 2 | 2 | False |
| `G8` | Best average returns over the last 20 years in the US | 5 | 1 | Stocks |
| `G44` | Growth needed to come out ahead if inflation is 5% | 3 | 3 | More than 5% |
| `G22` | Main advantage of index funds over active funds | 3 | 2 | Lower fees and expenses |
| `G11` | Why many municipal bonds pay lower yields | 3 | 3 | Municipal bonds can be tax-free |
| `G12` | $500 margin position, stock drops 50%, what remains | 3 | 3 | $0 |
| `G13` | Best definition of "selling short" | 4 | 4 | Selling borrowed shares of a stock |

**Option counts vary from 2 to 5**, so the chance rate ranges from .50 to .20. This is a property of the instrument that a summed score hides, and it is why the analysis includes an item audit rather than only a total.

---

## Derived measures

**The three tallies**, counted across the 11 items:

```
n_correct  = number of items answered with the correct code
n_dk       = number of items answered 98
n_pnts     = number of items answered 99
n_incorrect = 11 − n_correct − n_dk − n_pnts
```

`n_incorrect` is derived by subtraction and **excludes refusals**. That definition is not cosmetic: it is the one that reproduces FINRA's published figures. Under the strict definition the male and female incorrect counts are 3.31 and 3.33, both rounding to the published 3.3. Folding refusals into incorrect gives 3.36 and 3.41, which rounds to 3.4 and does not match.

An alternative measure, `n_incorrect_loose = 11 − n_correct − n_dk`, folds refusals in. It is used only in the robustness check on the looser sample rule.

**The compositional identity.** Within the analytic sample:

```
n_correct + n_incorrect + n_dk = 11
```

The three counts are linearly dependent. Once `n_correct` is in a model, `n_incorrect` and `n_dk` **cannot both enter**. The models use `f(n_correct, n_dk, X)`, and the `n_dk` coefficient is the incorrect-versus-DK substitution at fixed demonstrated knowledge. Anyone rebuilding this must respect that constraint, in any software.

---

## Outcome: G43

> If you heard about an investment opportunity that promises a guaranteed, risk-free 25% annual return every year for the next 5 years, would you invest in it?

Source codes: `1` Yes, `2` No, `98` Don't know, `99` Prefer not to say.

| Derived | Coding | Used in |
|---|---|---|
| `g43_3` | 1 = No (base), 2 = Don't know, 3 = Yes; refusals missing | Primary multinomial model |
| `g43_yes_all` | 1 = Yes, 0 = No or DK | Binary secondary |
| `g43_yes_no` | 1 = Yes, 0 = No; DK dropped | Binary secondary |

Refusals (about 0.2%) are set missing. A refusal to answer is not a fourth substantive response state.

**Placement matters.** G43 appears *before* the quiz in the instrument. Nothing here is temporal prediction, and the write-up uses "prediction" only in the out-of-sample sense.

---

## Self-assessed investing knowledge: G2

> On a scale from 1 to 7, where 1 means very low and 7 means very high, how would you assess your overall knowledge about investing?

Also asked **before** the quiz. Codes 98 and 99 are set missing rather than treated as scale points.

| Derived | Coding |
|---|---|
| `g2_scale` | 1–7 continuous |
| `g2_band` | 1 = Low (1–3), 2 = Neutral (4), 3 = High (5–7) |

---

## Covariates

The Investor Survey already carries demographics copied from the State-by-State survey. We verified these against the merged originals: agreement is 1.00 on sex, age, and education, with no missing values.

| Our name | Source | Coding |
|---|---|---|
| `sex` | `S_Gender2` | 1 Male, 2 Female |
| `agecat` | `S_Age` | 1 = 18–34, 2 = 35–54, 3 = 55+ |
| `educ` | `S_Education` | 1 = Some college or less, 2 = College graduate or more |
| `income` | `S_Income` | 1 = <$50K, 2 = $50K–$100K, 3 = $100K+ |
| `ethnicity` | `S_Ethnicity` | 1 = White non-Hispanic, 2 = Non-White |

These coarse bands are primary because they match the categories FINRA validates against. Finer alternatives from the merged State-by-State file are used in a robustness check: `a3ar_w_sbs` (6 age bands), `a5_2015_sbs` (7 education categories), `a8_2021_sbs` (10 income brackets).

Ethnicity enters the models as an adjustment. It is a binary collapse and the weight does not post-stratify on it, so its coefficient is not interpreted as a finding.

---

## Weight

`WGT1`, the Investor Survey weight. It post-stratifies on **age and education only**, so sex, income, and ethnicity are unadjusted in every weighted estimate.

The State-by-State weights (`wgt_n2`, `wgt_d2`, `wgt_s3`) are dropped during the build. They are built for the full 25,539-respondent sample; 8,933 respondents screened yes on `B14A_1` but only 2,861 completed the Investor Survey, and `WGT1` is what carries that subsampling correction.

FINRA does not release primary sampling units or strata, so design-based estimation here handles the weights under a with-replacement assumption and does not recover a clustered design.

---

## Samples

| Sample | n | Rule |
|---|---|---|
| Full | 2,861 | All Investor Survey respondents |
| Analytic | 2,797 | Drop anyone with ≥1 refusal on the 11 quiz items (64 respondents, 174 item refusals) |
| Predictive | 2,783 | Analytic, complete on every variable used in any nested model |

The refusal rule exists because `n_incorrect` is derived by subtraction: an unremoved refusal is silently reclassified as a wrong answer and breaks the sum-to-11 identity.

**The validation gate runs on the full 2,861, before the analytic rule is applied.** The published FINRA figures reproduce there and do not reproduce on the restricted sample — on 2,797 the female mean correct rises to 4.59, which rounds to 4.6 against a published 4.5. Reproducing published numbers and choosing an estimation sample are different questions, asked in that order.

---

## General non-quiz DK propensity

An auxiliary robustness measure: how often a respondent selected "don't know" on Investor Survey items unrelated to the knowledge quiz. It exists to check whether quiz DK merely reflects a general tendency to select DK elsewhere in the same instrument.

Three constructions are reported. The primary inferential model contains **no** non-quiz DK control; every version below is auxiliary.

### (a) 30-item measure — historical, as used in the published Stata run

```
nonquiz_dk_n     = count of 98 responses across the 30 items below
nonquiz_dk_share = nonquiz_dk_n / 30
```

**Items:** `A2`, `B30_2024`, `B3`, `B4_2024`, `B5`, `B33`, `B10`, `B40`, `B41`, `B23`, `C22_1`–`C22_4`, `C40`, `C23_1`–`C23_4`, `C24`, `C26`, `C7`, `D40`, `D31`, `D41`, `E2`, `E6`, `F40`, `G31`, `G42`.

Retained unchanged because the published Stata results were computed with it. A later audit found this list was not derived from an exhaustive eligibility rule — see `ANALYTICAL-DECISIONS.md` §14.

### (b) 69-item rule-derived measure — preferred measurement-sensitivity specification

An item is eligible iff, per the instrument's documented skip logic and the data dictionary:

1. it is administered to every continuing respondent (established from routing, **not** from patterns of nonmissing data);
2. it offers code 98 = "Don't know" as a substantive response option;
3. it is not a quiz item, not `G23`, not the outcome `G43`, not a variable used as a model covariate elsewhere (`G2`, `G40`, `G41`), and not an eligibility screener where selecting DK terminated the interview (`A1`, `A3`);
4. it is not an ID, weight, or demographic.

Applied to all 105 Investor Survey variables: **69 eligible, 36 excluded.** The item-by-item audit — with each item's construct, universality, the exact meaning of code 98, its DK-opportunity type, and the include/exclude reason — is in `docs/nonquiz-dk-item-audit.csv`.

Relative to (a), the rule adds 39 items in four grid blocks: `B2_*` ownership (11), `F30_*` reliance (11), `F31_*` platforms (11), `G30_*` motives (6).

```
idx69 = count of 98 responses across the 69 eligible items / 69
```

### (c) Battery-balanced version — additional sensitivity

Six eligible blocks are administered as grids (`B2`×11, `C22`×4, `C23`×4, `F30`×11, `F31`×11, `G30`×6 = 47 rows). Each remaining eligible item is its own block (22). Total: 28 blocks.

```
idx69_bal = mean across the 28 blocks of (DK responses in block / items in block)
```

An 11-row grid therefore carries the same weight as one stand-alone question.

### DK-opportunity types

Code 98 does not mean the same thing on every item. The 69 eligible items divide into:

| Type | Items | Example |
|---|---:|---|
| Behavioral self-report | 27 | How much do you rely on podcasts for investment decisions |
| Factual/account knowledge | 21 | Does your account permit margin |
| Attitudinal/self-description | 14 | People like me aren't usually investors |
| Recollection | 7 | Have you ever checked a regulator on a professional |

Sub-indices built from these four types are reported as **exploratory measurement diagnostics only**. They were not prespecified.

### Descriptives

| Measure | Items | Mean | SD | r with quiz `n_dk` |
|---|---:|---:|---:|---:|
| 30-item (historical) | 30 | .067 | .081 | .526 |
| 69-item rule-derived | 69 | .043 | .058 | .497 |
| 69-item battery-balanced | 69 | .063 | .071 | .539 |

### What this measures, and what it does not

It counts DK selections on non-quiz items. Several of those items involve genuine uncertainty about one's own finances — whether an account permits margin, which fees are paid, whether disclosures were received. A DK there may mean "I do not know this fact about my accounts."

This is not a validated response-style scale, and no output calls it one. The four sub-indices correlate only .20 to .64 with each other, which cautions against treating non-quiz DK as a unitary construct.

## Rebuilding this outside Stata

The measure is simple enough to reconstruct anywhere. In any language, the pattern is: compare each item to its key, sum the resulting true/false values.

**R**

```r
key <- c(G4=1, G5=2, G6=2, G7=1, G21=2, G8=1,
         G44=3, G22=2, G11=3, G12=3, G13=4)
items <- names(key)

d$n_correct <- rowSums(mapply(function(v, k) d[[v]] == k, items, key))
d$n_dk      <- rowSums(d[items] == 98)
d$n_pnts    <- rowSums(d[items] == 99)
d$n_incorrect <- 11 - d$n_correct - d$n_dk - d$n_pnts
```

For weighted estimation use the `survey` package: `svydesign(ids = ~1, weights = ~WGT1, data = d)`, then `svyglm()` or `svymean()`. For the three-category outcome, `nnet::multinom()` fits the model; `marginaleffects::avg_slopes()` converts coefficients to changes in probability.

**SPSS**

`COUNT` builds each tally in one line per response type. `NOMREG` fits the multinomial model. SPSS's base weighting is frequency weighting rather than design-based estimation, so weighted standard errors will differ from ours unless you have the Complex Samples module.

**Python**

`(df[items] == key_series).sum(axis=1)` for the tallies; `statsmodels.MNLogit` for the model. Our own Python scripts use `scikit-learn` for the prediction layer, and a purpose-built weighted multinomial fitter (`code/wmnl.py`) for the measurement-sensitivity models, because `MNLogit` does not accept sampling weights.

**Two traps when reading our exported CSV in Python.** The build exports value *labels* rather than numeric codes.

1. The label `"None"` is a legitimate response (`B3` = no trades in the past 12 months, 772 respondents), and pandas converts it to missing by default. Read with `pd.read_csv(..., keep_default_na=False)`.
2. `"Don't know"` arrives as a string, not the code 98. Item-level DK counts are built by matching the label.

---

*Questions or corrections: open an Issue or email householdfinancelab@gmail.com*
