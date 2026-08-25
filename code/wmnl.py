"""Weighted multinomial logit with sandwich (linearized) SEs — Stata svy: mlogit equivalent."""
import numpy as np
from scipy.optimize import minimize

def fit_wmnl(X, y, w, classes):
    """y coded 0..K-1, class 0 = base outcome."""
    n, p = X.shape; K = len(classes)
    def negll(b):
        B = b.reshape(K-1, p)
        eta = np.hstack([np.zeros((n,1)), X @ B.T])
        m = eta.max(1, keepdims=True)
        lse = m[:,0] + np.log(np.exp(eta-m).sum(1))
        return -np.sum(w * (eta[np.arange(n), y] - lse))
    b0 = np.zeros((K-1)*p)
    res = minimize(negll, b0, method='BFGS', options=dict(maxiter=2000, gtol=1e-10))
    b = res.x
    B = b.reshape(K-1, p)
    eta = np.hstack([np.zeros((n,1)), X @ B.T])
    m = eta.max(1, keepdims=True); e = np.exp(eta-m); P = e / e.sum(1, keepdims=True)
    # scores: for each equation k>=1, w_i*(d_ik - P_ik)*x_i
    S = np.zeros((n, (K-1)*p))
    for k in range(1, K):
        d = (y == k).astype(float)
        S[:, (k-1)*p:k*p] = (w * (d - P[:,k]))[:,None] * X
    meat = S.T @ S
    # Hessian (weighted, observed information)
    H = np.zeros(((K-1)*p, (K-1)*p))
    for a in range(1, K):
        for bq in range(1, K):
            wgt = w * (P[:,a]*((a==bq)-P[:,bq]))
            H[(a-1)*p:a*p, (bq-1)*p:bq*p] = X.T @ (wgt[:,None]*X)
    Hinv = np.linalg.inv(H)
    V = Hinv @ meat @ Hinv * (n/(n-1.0))
    return dict(b=b, V=V, P=P, B=B, n=n, p=p, K=K, X=X, w=w, converged=res.success)

def ame(fit, j, k):
    """AME of column j on P(outcome k). Delta method by numeric gradient."""
    X, w, K, p = fit['X'], fit['w'], fit['K'], fit['p']
    def amefun(b):
        B = b.reshape(K-1, p)
        eta = np.hstack([np.zeros((X.shape[0],1)), X @ B.T])
        m = eta.max(1, keepdims=True); e = np.exp(eta-m); P = e/e.sum(1, keepdims=True)
        beta_j = np.concatenate([[0.0], B[:, j]])
        wbar = P @ beta_j
        d = P[:, k] * (beta_j[k] - wbar)
        return np.sum(w*d)/np.sum(w)
    b = fit['b']; est = amefun(b)
    g = np.zeros_like(b)
    for i in range(len(b)):
        h = 1e-6*max(1.0, abs(b[i])); bp = b.copy(); bm = b.copy()
        bp[i]+=h; bm[i]-=h
        g[i] = (amefun(bp)-amefun(bm))/(2*h)
    se = float(np.sqrt(g @ fit['V'] @ g))
    return est, se
