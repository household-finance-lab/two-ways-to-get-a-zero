"""Household Finance Lab — Project 1: symmetric response-representation comparison."""
import pandas as pd
import numpy as np
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, roc_auc_score, accuracy_score

from paths import TABLES, require_analytic_csv

DATA = require_analytic_csv()
SEED = 20260818
N_SPLITS = 5
N_REPEATS = 10

df = pd.read_csv(DATA, low_memory=False)
needed = [
    "g43_3", "wgt1", "agecat", "educ", "income", "sex", "ethnicity",
    "n_correct", "n_dk", "n_incorrect", "g2_scale", "nonquiz_dk_share"
]
dat = df[needed].dropna().copy()
dat["y"] = dat["g43_3"].map({"No": 0, "Don't know": 1, "Yes": 2}).astype(int)

categorical = ["agecat", "educ", "income", "sex", "ethnicity"]
models = {
    "A Demographics": categorical,
    "B Demographics + Correct": categorical + ["n_correct"],
    "C Demographics + DK": categorical + ["n_dk"],
    "D Demographics + Incorrect": categorical + ["n_incorrect"],
    "E Full composition (Correct + DK)": categorical + ["n_correct", "n_dk"],
}

def weighted_multiclass_brier(y_true, proba, weights):
    y_onehot = np.eye(proba.shape[1])[y_true]
    return np.average(np.sum((proba - y_onehot) ** 2, axis=1), weights=weights)

def make_pipeline(cols):
    cat_cols = [c for c in cols if c in categorical]
    num_cols = [c for c in cols if c not in categorical]
    transformers = []
    if cat_cols:
        transformers.append(("cat", OneHotEncoder(drop="first", handle_unknown="ignore"), cat_cols))
    if num_cols:
        transformers.append(("num", StandardScaler(), num_cols))
    prep = ColumnTransformer(transformers=transformers, remainder="drop")
    model = LogisticRegression(solver="lbfgs", C=1.0, max_iter=3000)
    return Pipeline([("prep", prep), ("model", model)])

cv = RepeatedStratifiedKFold(n_splits=N_SPLITS, n_repeats=N_REPEATS, random_state=SEED)
splits = list(cv.split(dat, dat["y"]))
rows = []
oof_sums = {name: np.zeros((len(dat), 3)) for name in models}
oof_counts = np.zeros(len(dat))
for split_id, (train_idx, test_idx) in enumerate(splits):
    repeat = split_id // N_SPLITS + 1
    fold = split_id % N_SPLITS + 1
    train = dat.iloc[train_idx]
    test = dat.iloc[test_idx]
    oof_counts[test_idx] += 1
    for model_name, cols in models.items():
        pipe = make_pipeline(cols)
        pipe.fit(train[cols], train["y"].to_numpy(), model__sample_weight=train["wgt1"].to_numpy())
        proba = pipe.predict_proba(test[cols])
        y_test = test["y"].to_numpy()
        w_test = test["wgt1"].to_numpy()
        yhat = np.argmax(proba, axis=1)
        oof_sums[model_name][test_idx] += proba
        rows.append({
            "Model": model_name,
            "Repeat": repeat,
            "Fold": fold,
            "Log loss": log_loss(y_test, proba, labels=[0,1,2], sample_weight=w_test),
            "Brier": weighted_multiclass_brier(y_test, proba, w_test),
            "Macro AUC": roc_auc_score(y_test, proba, labels=[0,1,2], multi_class="ovr", average="macro", sample_weight=w_test),
            "Accuracy": accuracy_score(y_test, yhat, sample_weight=w_test),
        })
cv_results = pd.DataFrame(rows)
summary = cv_results.groupby("Model")[["Log loss", "Brier", "Macro AUC", "Accuracy"]].agg(["mean", "std"])
oof_avg = {name: oof_sums[name] / oof_counts[:, None] for name in models}
y = dat["y"].to_numpy()
w = dat["wgt1"].to_numpy()
class_names = ["No", "Don't know", "Yes"]
class_rows = []
for class_idx, class_name in enumerate(class_names):
    y_bin = (y == class_idx).astype(int)
    for model_name in models:
        class_rows.append({
            "Class": class_name,
            "Model": model_name,
            "One-vs-rest AUC": roc_auc_score(y_bin, oof_avg[model_name][:, class_idx], sample_weight=w),
        })
class_auc = pd.DataFrame(class_rows)
print(f"Common predictive sample: N={len(dat):,}")
print(summary.round(4))
print(class_auc.pivot(index="Model", columns="Class", values="One-vs-rest AUC").round(4))
# Flatten the MultiIndex columns for export so the committed table has a single
# header row. The console view above keeps the two-level layout.
summary_flat = summary.copy()
summary_flat.columns = [f"{metric} {stat}" for metric, stat in summary.columns]

cv_results.to_csv(TABLES / "symmetric_cv_fold_results.csv", index=False)
summary_flat.to_csv(TABLES / "prediction_symmetric_results.csv")
class_auc.to_csv(TABLES / "symmetric_class_auc.csv", index=False)
