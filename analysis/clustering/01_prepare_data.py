#!/usr/bin/env python3
"""
Prepare the dataset for clustering analysis (objective 3.2)
"""

# ## 1) Import libraries
import pandas as pd
from sklearn.preprocessing import StandardScaler
import numpy as np
import os
from config import (
    FEATURE_NAMES_PATH,
    HS_COLS,
    INPUT_DATA_PATH,
    OUTPUT_DIR,
    RAW_PATH,
    REVIEW_COLS,
    SCALED_PATH,
)

os.makedirs(OUTPUT_DIR, exist_ok=True)

# LOAD DATA
df = pd.read_csv(INPUT_DATA_PATH)

# ## 2. Select Variables

keep_cols = ["patient_id"] + HS_COLS + REVIEW_COLS
available_cols = [c for c in keep_cols if c in df.columns]
print(f" Found {len(available_cols)} variables to keep.")

df = df[available_cols]

# ## 3. Data Quality Check
summary = {
    "shape": df.shape,
    "missing": df.isna().sum().sort_values(ascending=False),
    "dtypes": df.dtypes,
    "numeric": df.describe().T,
}
print(summary)

# ## 4. Create Binary Review Indicators
for review_col in REVIEW_COLS:
    binary_col = review_col.replace("_date", "_bin")
    df[binary_col] = np.where(df[review_col].notna(), 1, 0)

df.drop(columns=REVIEW_COLS, inplace=True, errors="ignore")

print(df.loc[:, df.columns.str.contains("_bin")].describe().T)
for col in df.filter(like="_bin").columns:
    print(f"\n--- {col} ---")
    print(df[col].value_counts(dropna=False))

# ## 5. Scale and Save Data
binary_review_cols = [c for c in df.columns if c.endswith("_bin")]

# Scale
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df[HS_COLS])
scaled_df = pd.DataFrame(X_scaled, columns=HS_COLS, index=df.index)

# Combine scaled HS vars + binary reviews
df_scaled = pd.concat([df[["patient_id"]], scaled_df, df[binary_review_cols]], axis=1)

df.to_csv(RAW_PATH, index=False, compression="gzip")
df_scaled.to_csv(SCALED_PATH, index=False, compression="gzip")

print("Saved processed clustering datasets:")
print(f"   • Raw file:    {RAW_PATH}")
print(f"   • Scaled file: {SCALED_PATH}")
print("Data preparation complete.")
