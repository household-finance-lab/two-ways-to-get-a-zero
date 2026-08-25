# Measurement Sensitivity: the Non-Quiz DK Control

**Scope.** This exercise varies only how the auxiliary non-quiz DK measure is constructed. The primary inferential analysis, sample, weights, covariates, outcome coding, and specification are unchanged. Nothing here was tuned against G43.

**Sample.** n = 2,796 (analytic sample, valid G43), weighted by WGT1.

**Implementation.** Weighted multinomial logit fitted by maximum likelihood in Python with a sandwich covariance closely reproducing Stata's linearized estimates. Validated before use: base AME −.0467 (SE .0064); 30-item AME −.0423 (SE .0070); DK-equation coefficients on `n_dk` (+.0286, p = .519) and on the index (+4.4920, p < .001). Point estimates and standard errors match the Stata output to four decimals.

One inferential detail differs: intervals and p-values here use the normal distribution, while `svy:` reports t statistics on design degrees of freedom. At df ≈ 2,795 the difference is immaterial, which is why the outputs agree so closely, but this is a close reproduction rather than mathematical identity of every inferential quantity.

---

## A correction that comes first

An earlier reading of the Stata log stated that general non-quiz DK propensity "explains essentially all" of the association between quiz DK and answering *don't know* on G43. **That was wrong**, and the error was reading a coefficient as if it were a marginal effect.

Both of these are true and they answer different questions:

- In the **don't-know-versus-no equation**, the coefficient on `n_dk` falls from +.1007 to +.0286 (p = .519) when the 30-item index is added.
- The **average marginal effect on P(G43 = Don't know)** falls from +.0377 to +.0266 and remains significant at p < .001.

The AME is the study's stated primary quantity. The coefficient is a contrast against the *No* category alone; the AME accounts for the fact that `n_dk` also strongly reduces P(Yes), which mechanically raises P(Don't know).

The correct wording is: **adjustment for non-quiz DK responding attenuates the association between quiz DK and subsequently selecting DK on G43, but does not eliminate it.** Under the 30-item measure the AME declines from 3.77 to 2.66 percentage points, roughly one-third. The earlier statement, and anything written from it, needs correcting.

**Standing rule adopted from this error:** attenuation claims are made on the AME scale, because that is the study's stated estimand. A coefficient in one equation of a multinomial model is not a probability-scale association and must not be reported as one.

---

## The measurement rule, frozen before any outcome model ran

An item is eligible iff, per the instrument's documented skip logic and the data dictionary:

1. it is administered to every continuing respondent (established from routing, not from nonmissing data);
2. it offers code 98 = "Don't know" as a substantive option;
3. it is not a quiz item, not G23, not the outcome G43, not a covariate used elsewhere (G2, G40, G41), and not an eligibility screener where DK terminated the interview (A1, A3);
4. it is not an ID, weight, or demographic.

Applied to all 105 variables: **69 eligible, 36 excluded.** The complete audit is in `nonquiz-dk-item-audit.csv`.

**Why the earlier 30-item measure was under-inclusive.** It omitted 39 eligible items in four grid blocks — B2 ownership (11), F30 reliance (11), F31 platforms (11), G30 motives (6). The stated reason in the do-file was "to keep the index close to the earlier 26-item version," which is anchoring rather than a conceptual criterion. **The 26-item list could not be reconstructed from available materials and has not been guessed at.**

**DK opportunity is not one thing.** Among the 69 eligible items: behavioral self-report 27, factual/account knowledge 21, attitudinal/self-description 14, recollection 7. A DK on "does your account permit margin" is a different act from a DK on "how much do you rely on podcasts."

**Battery balancing, specified in advance.** Six blocks are grids (B2×11, C22×4, C23×4, F30×11, F31×11, G30×6 = 47 rows); the remaining 22 items are their own blocks. The balanced index is the unweighted mean across all 28 blocks of the within-block DK rate, so an 11-row grid carries the same weight as one stand-alone question.

---

## Measures

| Measure | Items | Mean | SD | Range | r with quiz `n_dk` |
|---|---:|---:|---:|---|---:|
| 30-item (as previously analyzed) | 30 | .0673 | .0813 | 0–.633 | .526 |
| Rule-derived, item-weighted | 69 | .0434 | .0583 | 0–.652 | .497 |
| Rule-derived, battery-balanced | 69 | .0631 | .0709 | 0–.593 | .539 |
| Sub-index: factual/account | 21 | .0953 | .1283 | 0–.905 | .464 |
| Sub-index: recollection | 7 | .0405 | .0854 | 0–.857 | .291 |
| Sub-index: attitudinal | 14 | .0268 | .0674 | 0–.714 | .367 |
| Sub-index: behavioral self-report | 27 | .0123 | .0482 | 0–.593 | .174 |

The three whole-index constructions correlate .87 to .97 with each other. The sub-indices are far less related to one another (.20 to .64), which is the first sign that "non-quiz DK" is not a single behavior.

---

## Results

**AME of quiz `n_dk` on P(G43 = Yes)**

| Specification | AME | SE | 95% CI | p | vs base |
|---|---:|---:|---|---:|---:|
| No non-quiz control (primary) | −.0467 | .0064 | [−.0592, −.0342] | <.001 | — |
| 30-item | −.0423 | .0070 | [−.0560, −.0286] | <.001 | +.0044 |
| Rule-derived, item-weighted | −.0411 | .0068 | [−.0545, −.0278] | <.001 | +.0055 |
| Rule-derived, battery-balanced | −.0417 | .0070 | [−.0555, −.0279] | <.001 | +.0050 |
| Sub-index: factual/account | −.0456 | .0068 | [−.0589, −.0324] | <.001 | +.0010 |
| Sub-index: recollection | −.0447 | .0065 | [−.0575, −.0319] | <.001 | +.0020 |
| Sub-index: attitudinal | −.0403 | .0067 | [−.0534, −.0272] | <.001 | +.0063 |
| Sub-index: behavioral self-report | −.0461 | .0063 | [−.0585, −.0337] | <.001 | +.0005 |

**AME of quiz `n_dk` on P(G43 = Don't know)**

| Specification | AME | SE | 95% CI | p | vs base |
|---|---:|---:|---|---:|---:|
| No non-quiz control (primary) | +.0377 | .0054 | [+.0271, +.0482] | <.001 | — |
| 30-item | +.0266 | .0058 | [+.0152, +.0380] | <.001 | −.0111 |
| Rule-derived, item-weighted | +.0297 | .0057 | [+.0185, +.0410] | <.001 | −.0079 |
| Rule-derived, battery-balanced | +.0255 | .0059 | [+.0140, +.0371] | <.001 | −.0121 |
| Sub-index: factual/account | +.0301 | .0056 | [+.0191, +.0410] | <.001 | −.0076 |
| Sub-index: recollection | +.0337 | .0056 | [+.0227, +.0446] | <.001 | −.0040 |
| Sub-index: attitudinal | +.0361 | .0057 | [+.0248, +.0473] | <.001 | −.0016 |
| Sub-index: behavioral self-report | +.0374 | .0054 | [+.0268, +.0480] | <.001 | −.0002 |

**AME of the non-quiz measure itself** (scaled per 1.0 = every item answered DK)

| Specification | on P(Yes) | p | on P(DK) | p |
|---|---:|---:|---:|---:|
| 30-item | −.225 | .227 | +.644 | <.001 |
| Rule-derived, item-weighted | −.531 | .046 | +.736 | <.001 |
| Rule-derived, battery-balanced | −.279 | .188 | +.764 | <.001 |
| Sub-index: factual/account | −.009 | .933 | +.351 | <.001 |
| Sub-index: recollection | −.190 | .190 | +.437 | <.001 |
| Sub-index: attitudinal | −.677 | .001 | +.221 | .128 |
| Sub-index: behavioral self-report | −.490 | .060 | +.206 | .265 |

---

## The four questions

**1. Does the primary quiz-DK → P(Yes) association materially depend on the construction of the non-quiz DK control?**

No. Across all eight specifications it ranges from −.0403 to −.0467, every interval excludes zero, every p < .001, and the confidence intervals overlap almost completely. The largest movement from the uncontrolled estimate is 0.6 percentage points — well inside the sampling uncertainty of a single estimate (SE ≈ .007). Adding any non-quiz DK control attenuates the association slightly and leaves it intact.

**2. Does the conclusion about P(G43 = Don't know) change?**

Yes — relative to the earlier, mistaken characterization. Under every construction the AME attenuates (by 0.4 to 1.2 percentage points, i.e. 10% to 32%) and remains firmly significant. The correct statement is that a general propensity to select DK elsewhere accounts for **part but not most** of the association between quiz DK and withholding judgment on G43.

The attenuation is generally larger for P(Don't know) than for P(Yes). The whole-index measures are consistently associated with selecting DK on G43, while the domain-specific sub-indices differ substantially — the attitudinal (p = .128) and behavioral self-report (p = .265) sub-indices are not. This heterogeneity reinforces that non-quiz DK should not be treated as a single validated response-style construct.

**3. How much does grid/battery weighting matter?**

Very little for the conclusions, a little for the measure. Balancing raises the correlation with quiz DK (.497 → .539), because down-weighting the two large social-media and reliance grids concentrates the measure on account-knowledge items. On the outcomes, item-weighted and balanced versions differ by .0006 on P(Yes) and .0042 on P(DK) — smaller than one standard error in both cases. The battery-weighting concern is legitimate in principle and immaterial here.

**4. Should the repo retain, replace, or report both?**

**Report both**, retaining the 30-item specification as the originally reported robustness analysis and designating the rule-derived 69-item measure as the preferred measurement-sensitivity specification.

The word "primary" belongs to the model with no non-quiz control at all. The non-quiz measure is auxiliary; calling any version of it primary would misstate the study's hierarchy, which is:

| Level | Specification |
|---|---|
| Primary inferential model | No non-quiz DK control |
| Original robustness | 30-item non-quiz DK measure |
| Preferred measurement-sensitivity specification | 69-item rule-derived measure |
| Additional sensitivity | Battery-balanced 69-item version |
| Exploratory measurement diagnostics | Four DK-opportunity sub-indices |

The 30-item measure stays because your published Stata results were computed with it, so removing it would break the correspondence between the log and the write-up. Both give the same answer, so nothing is hidden by showing both.

---

## What these measures can and cannot be called

They count how often a respondent selected "don't know" on non-quiz Investor Survey items. Nothing here establishes them as a validated scale, and they are not called response style, satisficing, uncertainty recognition, or metacognition anywhere in this document.

The sub-indices behave differently from one another. The attitudinal sub-index is independently associated with P(Yes) (−.677, p = .001) while the factual/account sub-index is not (−.009, p = .933); the factual sub-index is associated with P(Don't know) while the attitudinal one is not. The four correlate only .20 to .64 with each other, and their correlations with quiz DK range from .174 to .464.

This is suggestive evidence of heterogeneity rather than a falsification of a single latent tendency. Multiple noisy indicators of one underlying disposition can diverge because of domain, item format, reliability, base rates, and measurement error. The defensible statement is that **the heterogeneous sub-index patterns caution against treating non-quiz DK as a unitary response-style construct and strengthen the case for measuring the underlying mechanisms directly in a future experiment.**

None of this was prespecified. It is a measurement observation, not a finding.

---

## Two things for the reproducibility record

**The exported CSV has a silent missing-data trap.** Value labels include the string `"None"` (B3 = "None" trades in 12 months, 772 respondents). Pandas converts that to missing under default settings. Any Python reading the labeled export needs `keep_default_na=False`. The existing prediction scripts are unaffected — they use only numeric derived variables and the G43 labels — but this belongs in `data/README.md` before anyone else runs the file.

**The 26-item measure remains unreconstructed.** It is documented as superseded rather than compared, because guessing its composition to produce a comparison would be worse than reporting its absence.
