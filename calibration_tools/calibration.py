#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel → Curve Fitting (Y = f(X)) → Equation Printer + Evaluator

Usage examples:
  1) Polynomial degree-3 fit (default sheet, by column names):
     python curve_fit_from_excel.py --file roadcell_lookup_table.xlsx --xcol X --ycol Y --degree 3 --model poly

  2) Exponential fit y = a * exp(b x):
     python curve_fit_from_excel.py --file roadcell_lookup_table.xlsx --xcol 0 --ycol 1 --model exp

  3) Interactive evaluate after fit:
     python curve_fit_from_excel.py --file roadcell_lookup_table.xlsx --xcol X --ycol Y --degree 2 --interactive

Notes
- Columns can be specified by name or index (0-based).
- Supported models:
    * poly  : y = a_n x^n + ... + a_1 x + a_0  (n = degree)
    * exp   : y = a * exp(b x)                  (requires y > 0)
    * power : y = a * x^b                       (requires x > 0, y > 0)
    * log   : y = a + b * ln(x)                 (requires x > 0)
- Outputs a summary file: fit_result.txt (in the current working dir).
"""

import argparse
import math
import sys
from typing import Tuple, Callable, Dict, Any

import numpy as np
import pandas as pd

# --------------------------- Utilities ---------------------------

def _resolve_column(df: pd.DataFrame, col_spec: str) -> str:
    """Return a valid column name from a specification (name or index str)."""
    if col_spec.isdigit():
        idx = int(col_spec)
        if idx < 0 or idx >= len(df.columns):
            raise ValueError(f"Column index out of range: {idx}")
        return df.columns[idx]
    # otherwise treat as name
    if col_spec not in df.columns:
        raise ValueError(f"Column name not found: {col_spec}. Available: {list(df.columns)}")
    return col_spec

def r2_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return 1 - ss_res / ss_tot if ss_tot > 0 else float('nan')

def format_polynomial(coeffs: np.ndarray) -> str:
    """Return polynomial as human-friendly string: a_n x^n + ... + a0"""
    terms = []
    n = len(coeffs) - 1
    for i, a in enumerate(coeffs):
        p = n - i
        coef = f"{a:.6g}"
        if p == 0:
            terms.append(f"{coef}")
        elif p == 1:
            terms.append(f"{coef}·x")
        else:
            terms.append(f"{coef}·x^{p}")
    return " + ".join(terms).replace("+ -", "- ")

# --------------------------- Models ---------------------------

def fit_poly(x: np.ndarray, y: np.ndarray, degree: int) -> Tuple[Callable[[np.ndarray], np.ndarray], Dict[str, Any]]:
    coeffs = np.polyfit(x, y, degree)
    f = np.poly1d(coeffs)
    y_pred = f(x)
    info = {
        "model": "poly",
        "degree": degree,
        "coeffs": coeffs.tolist(),
        "equation": "y = " + format_polynomial(coeffs),
        "R2": float(r2_score(y, y_pred))
    }
    return (lambda X: f(X)), info

def fit_exp(x: np.ndarray, y: np.ndarray) -> Tuple[Callable[[np.ndarray], np.ndarray], Dict[str, Any]]:
    # y = a * exp(bx) -> ln(y) = ln(a) + b x
    if np.any(y <= 0):
        raise ValueError("Exponential model requires y > 0 for all data points.")
    Y = np.log(y)
    b, ln_a = np.polyfit(x, Y, 1)  # slope = b, intercept = ln(a)
    a = math.exp(ln_a)
    def f(X): return a * np.exp(b * X)
    y_pred = f(x)
    info = {
        "model": "exp",
        "params": {"a": a, "b": b},
        "equation": f"y = {a:.6g} · exp({b:.6g}·x)",
        "R2": float(r2_score(y, y_pred))
    }
    return f, info

def fit_power(x: np.ndarray, y: np.ndarray) -> Tuple[Callable[[np.ndarray], np.ndarray], Dict[str, Any]]:
    # y = a * x^b -> ln(y) = ln(a) + b ln(x)
    if np.any(x <= 0) or np.any(y <= 0):
        raise ValueError("Power model requires x > 0 and y > 0 for all data points.")
    X = np.log(x)
    Y = np.log(y)
    b, ln_a = np.polyfit(X, Y, 1)
    a = math.exp(ln_a)
    def f(U): return a * (U ** b)
    y_pred = f(x)
    info = {
        "model": "power",
        "params": {"a": a, "b": b},
        "equation": f"y = {a:.6g} · x^{b:.6g}",
        "R2": float(r2_score(y, y_pred))
    }
    return f, info

def fit_log(x: np.ndarray, y: np.ndarray) -> Tuple[Callable[[np.ndarray], np.ndarray], Dict[str, Any]]:
    # y = a + b ln(x)
    if np.any(x <= 0):
        raise ValueError("Log model requires x > 0 for all data points.")
    L = np.log(x)
    b, a = np.polyfit(L, y, 1)
    def f(U): return a + b * np.log(U)
    y_pred = f(x)
    info = {
        "model": "log",
        "params": {"a": a, "b": b},
        "equation": f"y = {a:.6g} + {b:.6g} · ln(x)",
        "R2": float(r2_score(y, y_pred))
    }
    return f, info

FITTERS = {
    "poly": fit_poly,
    "exp": lambda x, y, degree=None: fit_exp(x, y),
    "power": lambda x, y, degree=None: fit_power(x, y),
    "log": lambda x, y, degree=None: fit_log(x, y),
}

# --------------------------- Main ---------------------------

def main():
    p = argparse.ArgumentParser(description="Excel curve fitting: read X,Y and print Y=f(X) equation.")
    p.add_argument("--file", required=True, help="Path to Excel file (.xlsx, .xls).")
    p.add_argument("--sheet", default=0, help="Sheet name or index (default: 0).")
    p.add_argument("--xcol", required=True, help="X column (name or 0-based index).")
    p.add_argument("--ycol", required=True, help="Y column (name or 0-based index).")
    p.add_argument("--model", choices=list(FITTERS.keys()), default="poly", help="Fit model type.")
    p.add_argument("--degree", type=int, default=2, help="Degree for polynomial model (default: 2).")
    p.add_argument("--dropna", action="store_true", help="Drop rows with NaN in X or Y.")
    p.add_argument("--interactive", action="store_true", help="After fitting, repeatedly accept X and print predicted Y.")
    p.add_argument("--autoscale", action="store_true", help="Auto-scale X,Y to [0,1] before fitting (poly only), improves conditioning.")
    p.add_argument("--save", default="fit_result.txt", help="Path to save a short summary (default: fit_result.txt).")
    args = p.parse_args()

    # Load Excel
    try:
        sheet = int(args.sheet) if str(args.sheet).isdigit() else args.sheet
        df = pd.rea
