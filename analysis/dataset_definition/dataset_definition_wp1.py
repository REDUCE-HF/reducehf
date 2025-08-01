from ehrql import create_dataset
from dataset_definition import generate_dataset

dataset = create_dataset()

dataset.configure_dummy_data(population_size=100000)

#placeholder dates for now
project_index_date = "2020-01-01"
start_date = "2020-01-01"
end_date = "2025-01-01"

# could also add WP specific covariates here

dataset = generate_dataset(project_index_date, start_date, end_date)