

import pandas as pd
import config 
import os

df = pd.read_csv("../../output/dataset_wp4.csv.gz", compression='gzip')


date_columns = [col for col in df.columns if "_date" in col]
df[date_columns] = df[date_columns].apply(pd.to_datetime)


main_cols = [
    "patient_id",
    "sex",
    "ethnicity_cat",
    "index_date",
    "birth_date",
    "sysbp_value",
    "bmi_value",
    "last_cholesterol_value",
    "last_hdl_cholesterol_value",
    "last_hba1c_value",
    "fasting_blood_glucose_value",
    "smoking",
    "last_hypertension_date_med",
    "last_diabetes_medication_date",
    "hf_diagnosis_date"
]
df_main = df[main_cols]