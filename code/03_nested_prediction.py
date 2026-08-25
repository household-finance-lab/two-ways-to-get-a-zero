"""Household Finance Lab — Project 1: nested predictive analysis."""
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
features_needed = [
    "g43_3", "wgt1", "agecat", "educ", "income", "sex", "ethnicity",
    "n_correct", "n_dk", "g2_scale", "nonquiz_dk_share"
]
pred = df[features_needed].dropna().copy()
pred["y"] = pred["g43_3"].map({"No": 0, "Don't know": 1, "Yes": 2}).astype(int)

categorical = ["agecat", "educ", "income", "sex", "ethnicity"]
models = {
    "A Demographics": categorical,
    "B + Correct": categorical + ["n_correct"],
    "C + Quiz DK": categorical + ["n_correct", "n_dk"],
    "D + Self-assessed knowledge": categorical + ["n_correct", "n_dk", "g2_scale"],
    "E + Non-quiz DK propensity": categorical + ["n_correct", "n_dk", "g2_scale", "nonquiz_dk_share"],
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
splits = list(cv.split(pred, pred["y"]))
rows = []
for model_name, cols in models.items():
    for split_id, (train_idx, test_idx) in enumerate(splits):
        repeat = split_id // N_SPLITS + 1
        fold = split_id % N_SPLITS + 1
        train = pred.iloc[train_idx]
        test = pred.iloc[test_idx]
        pipe = make_pipeline(cols)
        pipe.fit(train[cols], train["y"].to_numpy(), model__sample_weight=train["wgt1"].to_numpy())
        proba = pipe.predict_proba(test[cols])
        y_test = test["y"].to_numpy()
        w_test = test["wgt1"].to_numpy()
        yhat = np.argmax(proba, axis=1)
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
print(f"Common predictive sample: N={len(pred):,}")
print(summary.round(4))
cv_results.to_csv(TABLES / "nested_cv_fold_results.csv", index=False)
summary.to_csv(TABLES / "nested_cv_summary.csv")
