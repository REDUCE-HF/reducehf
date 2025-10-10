# Prepare the dataset for clustering analysis (objective 3.2)

import pandas as pd 
from sklearn.preprocessing import StandardScaler
import numpy as np
import os

INPUT_PATH = "output/dataset_wp3.csv.gz"  
OUTPUT_DIR = "output/clustering/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------LOAD DATA--------------------
print("Loading dataset... ")
df = pd.read_csv(INPUT_PATH)

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

# CREATE count for REVIEW VARIABLES 
# If review date exists  1, else 0
for review_col in review_cols:
    if review_col in df.columns:
        df["review_count"] = df[review_cols].notna().sum(axis=1)


#  Drop the date versions (keep only binary)
df.drop(columns=[c for c in review_cols if c in df.columns], inplace=True, errors="ignore")

#  SCALE hs VARIABLES
all_count_cols = hs_cols + ["review_count"]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(df[all_count_cols])
scaled_df = pd.DataFrame(X_scaled, columns=all_count_cols, index=df.index)

# ---------- COMBINE AND SAVE ----------
df_scaled = pd.concat([df[["patient_id"]], scaled_df], axis=1)

raw_out = os.path.join(OUTPUT_DIR, "clustering_raw.csv.gz")
scaled_out = os.path.join(OUTPUT_DIR, "clustering_scaled.csv.gz")

df.to_csv(raw_out, index=False, compression="gzip")
df_scaled.to_csv(scaled_out, index=False, compression="gzip")

print("Saved processed clustering datasets:")
print(f"   • Raw file:    {raw_out}")
print(f"   • Scaled file: {scaled_out}")
print("Data preparation complete.")