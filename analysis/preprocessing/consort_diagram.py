import pandas as pd

df = pd.read_csv('output/dataset_consort.csv.gz')

start_date = pd.to_datetime('2020-01-01', format = '%Y-%m-%d')
end_date = pd.to_datetime('2025-05-01', format = '%Y-%m-%d')
df.patient_index_date = pd.to_datetime(df.patient_index_date)
df.death_date = pd.to_datetime(df.death_date)


exclusion_steps = {}

exclusion_steps['start'] = [df.shape[0]]

# missing dob

df['dob'] = pd.to_datetime(df.dob, format = '%Y-%m-%d')

df = df.loc[~df.dob.isna()]

exclusion_steps['missing_dob'] = [df.shape[0]]


# missing sex

df = df.loc[df.sex.isin(['male','female'])]

exclusion_steps['missing_sex'] = [df.shape[0]]


# < 45 on end_date

df['diff'] = (end_date - df['dob']).dt.days/365.25

df = df.loc[df['diff']>=45]

exclusion_steps['under_45'] = [df.shape[0]]


# > 110 on patient_index_date

df['diff'] = (df.patient_index_date - df['dob']).dt.days/364.25

df = df.loc[df['diff']<=110]

exclusion_steps['over_110'] = [df.shape[0]]


# dies before start

df = df.loc[((df.death_date > df.patient_index_date) | (df.death_date.isna()))]

exclusion_steps['dies_before_eligibility'] = [df.shape[0]]

# no IMD

df = df.loc[~df.imd10.isna()]

exclusion_steps['missing_imd'] = [df.shape[0]]


# no rural/urban classification

df = df.loc[~df.rural_urban.isna()]

exclusion_steps['missing_rural_urban'] = [df.shape[0]]


# Male and pregnant/hrt

df = df.loc[~((df.sex=='male') & (~df.pregnancy.isna()|~df.hrtcocp.isna()))]

exclusion_steps['male_pregnant_hrt'] = [df.shape[0]]


# Female and prostate cancer

df = df.loc[~((df.sex=='female') & ~(df.prostate_cancer.isna()))]

exclusion_steps['female_prostate'] = [df.shape[0]]


# add HF stats

# DO WE WANT N WITH HF DIAGNOSIS??

df = df.loc[df.hf_exclude.isna()]

exclusion_steps['hf_evidence_pre_eligibility'] = [df.shape[0]]


# save to csv

exclusion_df = pd.DataFrame.from_dict(exclusion_steps, orient='index', columns = ['new_sample_size'])
exclusion_df['n_excluded'] = exclusion_df.new_sample_size.diff()

exclusion_df.to_csv('output/consort_diagram_dta.csv')

