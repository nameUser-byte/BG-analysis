---
name: Photo PR Data Preprocessing & Modeling Pipeline
description: Standardized rules and steps for processing Photo Resist lithography data, modeling Critical Dimension (CD), and evaluating Pass/Fail limits.
---

# Photo PR Pipeline Skill

This skill defines the standardized preprocessing rules and machine learning strategy for the Photo PR dataset to ensure reproducibility across different subsets of data (e.g. train, test, holdout).

## 1. Data Cleaning & Preprocessing Rules

When a new dataset (e.g. `holdout_features.csv`) is provided, apply the following steps in exact order:

### A. Deduplication and Initial Filtering
- Remove duplicate columns (e.g., `df.loc[:, ~df.columns.duplicated()]`).
- (If training data) Remove completely duplicated rows (`df.drop_duplicates()`).
- (If training data) Drop any row where the key categorical variable `pr_tone` is missing.

### B. Physical Outlier Correction
Replace physically impossible values with `NaN` so they can be imputed properly later. Do NOT drop the rows.
- **Exposure Dose**: `exposure_dose_mj_cm2` > 300 $mJ/cm^2 \rightarrow$ `NaN`
- **Post-Exposure Bake (PEB) Temp**: `peb_temp_c` > 300 $\text{°C} \rightarrow$ `NaN`
- **Probabilities**: Clip `scum_probability`, `pattern_collapse_probability`, `defect_probability` to exactly `[0.0, 1.0]`.

### C. Imputation (Conditional Median)
- Group data by `['pr_tone', 'tool_id']`.
- Calculate the median for all numeric continuous variables.
- Fill `NaN` values (including the outliers converted in Step B) with these conditional medians.
- *Hold-out Constraint*: If evaluating holdout data, use the medians calculated from the *training* data to prevent data leakage. If a `(pr_tone, tool_id)` combination is unseen, fallback to the `pr_tone` level median, or the global median.

## 2. Multicollinearity Handling

- Never use `normalized_dose_pct` and `exposure_dose_mj_cm2` together. They exhibit severe multicollinearity (VIF > 27).
- Drop `normalized_dose_pct`. The remaining features (focus, coat thickness, bake temps, develop time, developer conc.) will have VIF ~1.0.

## 3. Modeling Strategy (PR Tone Splitting)

The chemical mechanisms of Positive and Negative PR are fundamentally different. Data must be split and modeled separately.

- **NEGATIVE PR**: Use tree ensembles like `Random Forest` or `XGBoost`. Negative PR typically shows higher predictability (R² ~ 0.65 - 0.70).
- **POSITIVE PR**: Use gradient boosting algorithms optimized for complex non-linear interactions like `LightGBM`. Predictability is generally lower (R² ~ 0.50 - 0.57) due to high susceptibility to Scum defects.

## 4. Evaluation & Verification

- Predict `resist_line_cd_nm` (CD).
- Compare the predicted CD against the empirical Pass/Fail specification limit derived from the training data (e.g. 43.65 nm ~ 56.22 nm).
- Calculate final yield (Pass rate) based on this logical condition rather than training a separate classifier, as CD is the primary physical constraint.
