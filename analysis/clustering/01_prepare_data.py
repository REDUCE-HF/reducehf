# Prepare the dataset for clustering analysis (objective 3.2)

import pandas as pd 
from sklearn.preprocessing import StandardScaler
import numpy as np
import os
from config import (
    FEATURE_NAMES_PATH,
    INPUT_DATA_PATH,
    OUTPUT_DIR,
    RAW_PATH,
    SCALED_PATH,
)

os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------LOAD DATA--------------------
print("Loading dataset... ")
df = pd.read_csv(INPUT_DATA_PATH)

# ---------- SELECT VARIABLES ----------

# Pre-index health service variables
hs_cols = [
    "ed_attendances_pre_0_3m",
    "ed_attendances_pre_3_6m",
    "ed_attendances_pre_6_9m",
    "ed_attendances_pre_9_12m",
    "primary_care_attendances_pre_0_3m",
    "primary_care_attendances_pre_3_6m",
    "primary_care_attendances_pre_6_9m",
    "primary_care_attendances_pre_9_12m",
    "hospital_admissions_pre_0_3m",
    "hospital_admissions_pre_3_6m",
    "hospital_admissions_pre_6_9m",
    "hospital_admissions_pre_9_12m",
    "prescriptions_pre_0_3m",
    "prescriptions_pre_3_6m",
    "prescriptions_pre_6_9m",
    "prescriptions_pre_9_12m",
]
# Review variables 
review_cols = [
    "asthma_review_date",
    "copd_review_date",
    "med_review_date",
]

keep_cols = ["patient_id"] + hs_cols + review_cols
available_cols = [c for c in keep_cols if c in df.columns]
print(f" Found {len(available_cols)} variables to keep.")

df = df[available_cols].copy()


# Replace NaN in  counts with 0
for col in hs_cols:
    if col in df.columns:
        df[col] = df[col].fillna(0)

# Create binary review indicators
for review_col in review_cols:
    if review_col in df.columns:
        binary_col = review_col.replace("_date", "_bin")
        df[binary_col] = np.where(df[review_col].notna(), 1, 0)

# Drop date versions
df.drop(columns=review_cols, inplace=True, errors="ignore")

# Updated variable list
binary_review_cols = [c for c in df.columns if c.endswith("_bin")]
all_vars = hs_cols + binary_review_cols

# Save feature names for later df reconstruction 
with open(FEATURE_NAMES_PATH, 'w') as f:
    for item in all_vars:
        f.write(f"{item}\n")
print(f"Saved feature names to: {FEATURE_NAMES_PATH}")
# -------------------------------------------------
# Scale 
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df[hs_cols])
scaled_df = pd.DataFrame(X_scaled, columns=hs_cols, index=df.index)

# Combine scaled HS vars + binary reviews
df_scaled = pd.concat([df[["patient_id"]], scaled_df, df[binary_review_cols]], axis=1)


df.to_csv(RAW_PATH, index=False, compression="gzip")
df_scaled.to_csv(SCALED_PATH, index=False, compression="gzip")

print("Saved processed clustering datasets:")
print(f"   • Raw file:    {RAW_PATH}")
print(f"   • Scaled file: {SCALED_PATH}")
print("Data preparation complete.")
