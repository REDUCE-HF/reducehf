import os
import pandas as pd
import numpy as np

from clustering_helpers import get_best_config, get_diagnosis_location
from sklearn.tree import DecisionTreeClassifier
from config import (
    INPUT_DATA_PATH,
    VALIDATION_RESULTS_PATH,
    VARIANCE_OF_MEANS_PATH,
    labels_path
)

def build_membership_features(df):
    """Build membership features for cluster characterization."""
    out = pd.DataFrame({"patient_id": df["patient_id"]})

    #  (todo preprocessing step to ensure all columns have correct type and possible rename appropriately)??
    # Convert all date columns to datetime
    date_cols = [
        "patient_index_date", "birth_date",
        "first_copd_date", "tmp_copd_date_primary", "tmp_copd_date_sus",
        "hypertension_date_primary", "hypertension_date_sus", "hypertension_date_med",
        "af_date_primary", "af_date_sus",
        "ihd_date_primary", "ihd_date_sus",
        "ckd_date_primary", "ckd_date_sus",
        "obesity_primary_date", "obesity_sus_date",
        "bmi_date",
        "learndis",
        "hf_diagnosis_primary_date", "hf_diagnosis_emerg_date", 
        "hf_diagnosis_ec_date", "hf_diagnosis_apc_date","hf_diagnosis_date"
    ]
    dates_df = {col: pd.to_datetime(df[col], errors="coerce") 
             for col in date_cols if col in df.columns}
    
    # Diagnosis location
    out["diagnosis_community"], out["diagnosis_emergency"] = get_diagnosis_location(df)
    
    # Age bands
    age = np.floor((dates_df["patient_index_date"] - dates_df["birth_date"]).dt.days / 365.25)
    age_bins = [0, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 120]
    age_labels = ['<45', '45-49', '50-54', '55-59', '60-64', '65-69', '70-74', 
                  '75-79', '80-84', '85-89', '90-94', '95-99', '100+']
    out["age_band"] = pd.cut(age, bins=age_bins, labels=age_labels, right=False).astype("object")
    
    # Categorical variables
     # Household size (categorised)
    hs_numeric = pd.to_numeric(df["household_size"], errors="coerce")
    out["cat_household_size"] = pd.cut(
        hs_numeric,
        bins=[0, 1, 2, np.inf],
        labels=["1", "2", ">=3"],
        right=True,
        include_lowest=True
    ).astype("object")

    out.loc[hs_numeric.isna() | (hs_numeric <= 0), "cat_household_size"] = "unknown"

    categorical_cols = ["sex", "ethnicity_cat", "imd_quintile", "region", 
                        "rural_urban", "cat_diabetes", "smoking","cat_household_size"]
    for col in categorical_cols:
        if col in df.columns:
            out[col] = df[col].astype("object")
    
   
    
    # Binary conditions from dates
    date_based_conditions = {
        "copd": ["first_copd_date", "tmp_copd_date_primary", "tmp_copd_date_sus"],
        "hypertension": ["hypertension_date_primary", "hypertension_date_sus", "hypertension_date_med"],
        "af": ["af_date_primary", "af_date_sus"],
        "ihd": ["ihd_date_primary", "ihd_date_sus"],
        "ckd": ["ckd_date_primary", "ckd_date_sus"],
        "learndis": ["learndis"],
    }
    # Create pre_existing and new conditions based on 1 year before hf diagnosis
    hf_diagnosis_date = dates_df["hf_diagnosis_date"]
    
    for condition, cols in date_based_conditions.items():
        condition_dates = pd.DataFrame({c: dates_df.get(c) for c in cols if c in dates_df})
        
        if not condition_dates.empty:
            first_date = condition_dates.min(axis=1)
            out[f"{condition}_preexisting"] = (first_date < (hf_diagnosis_date - pd.Timedelta(days=365))).fillna(False).astype(int)
            out[f"{condition}_new"] = ((first_date >= (hf_diagnosis_date - pd.Timedelta(days=365))) & (first_date <= hf_diagnosis_date)).fillna(False).astype(int)
            # out[condition] = condition_dates.notna().any(axis=1).astype(int)    # Keep or drop ? 
        else:
            out[f"{condition}_preexisting"] = 0
            out[f"{condition}_new"] = 0
            # out[condition] = 0  # Keep or drop ? 
    
    # Obesity: combine date-based (obesity_primary_date, obesity_sus_date) and BMI-based (≥30)
    obesity_date_cols = ["obesity_primary_date", "obesity_sus_date"]
    obesity_dates = pd.DataFrame({c: dates_df.get(c) for c in obesity_date_cols if c in dates_df})
    obesity_from_dates = obesity_dates.notna().any(axis=1).astype(int) if not obesity_dates.empty else 0
    obesity_bmi = (pd.to_numeric(df["bmi_value"], errors="coerce") >= 30).fillna(False).astype(int)
    out["obesity"] = ((obesity_from_dates == 1) | (obesity_bmi == 1)).astype(int)
    
    # Diabetes
    out["has_diabetes"] = (df["cat_diabetes"] != "DM unlikely").astype(int)
    
    # Multi-morbidity
    ltc_cols = ["copd_preexisting", "copd_new", "hypertension_preexisting", "hypertension_new", 
                "obesity", "af_preexisting", "af_new", "ihd_preexisting", "ihd_new", 
                "ckd_preexisting", "ckd_new", "has_diabetes"]
    out["mltc_count"] = out[ltc_cols].sum(axis=1)
    out["has_mltc"] = (out["mltc_count"] >= 2).astype(int)
    
    # Under-served groups
    underserved_cols = ["carehome_at_index", "housebound", "smi", "homeless", 
                        "substance_abuse", "migrant", "non_english_speaking"]
    for col in underserved_cols:
        if col in df.columns:
            out[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    
    return out.dropna(axis=1, how="all")

def variance_of_means(labels, X):
    """Calculate variance of cluster means for each feature."""
    df = X.assign(cluster=labels)
    df = df[df["cluster"] != -1]
    return df.groupby("cluster").mean(numeric_only=True).var()


def main():
    """Main execution function."""
    best_config = get_best_config(VALIDATION_RESULTS_PATH)
    print(f"Best configuration: {best_config}")

    labels_df = pd.read_csv(labels_path(best_config), compression="gzip")
    wp3_df = pd.read_csv(INPUT_DATA_PATH)

    df = wp3_df.merge(labels_df, on="patient_id", how="inner")
    print(f"Merged {len(df)} patients with cluster labels")

    membership = build_membership_features(df)
    print(f"Built {len(membership.columns)-1} membership features")

    # Define output directory from VARIANCE_OF_MEANS_PATH
    output_dir = os.path.dirname(VARIANCE_OF_MEANS_PATH)
    os.makedirs(output_dir, exist_ok=True)

    membership_path = os.path.join(output_dir, "membership_features.csv")
    membership.to_csv(membership_path, index=False)
    print(f"Saved membership features to {membership_path}")

    # One-hot encode categorical variables
    X = pd.get_dummies(membership.drop(columns="patient_id"), dummy_na=True, drop_first=False)

    # Identify continuous vs dummy columns
    continuous_vars = ['mltc_count']
    continuous_cols = [col for col in X.columns if col in continuous_vars]
    dummy_cols = [col for col in X.columns if col not in continuous_cols]

    print(f"After one-hot encoding: {len(X.columns)} features "
          f"({len(continuous_cols)} continuous, {len(dummy_cols)} dummy)")

    encoded_path = os.path.join(output_dir, "membership_features_encoded.csv")
    X.to_csv(encoded_path, index=False)
    print(f"Saved one-hot encoded features to {encoded_path}")

    # Calculate variance of means
    vom = variance_of_means(df["cluster"], X)
    vom.sort_values(ascending=False).to_csv(VARIANCE_OF_MEANS_PATH, header=["variance_of_means"])

    print(f"\nSaved: {VARIANCE_OF_MEANS_PATH}")
    print(f"\nTop 10 most discriminative features:")
    print(vom.sort_values(ascending=False).head(10))
    print(sorted([col for col in df.columns if '_date' in col]))
    # print (X.columns)

if __name__ == "__main__":
    main()