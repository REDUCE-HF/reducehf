"""
Helpers for optimisation to avoid repeating code for each method. 
"""

import os
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    brier_score_loss,
    ConfusionMatrixDisplay,
)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sdc_helpers import DISCLOSURE_THRESHOLD, apply_sdc_to_counts

from config_models import (
    TRAIN_DATA_PATH,
    TEST_DATA_PATH,
    TRAIN_SUBGROUP_DATA_PATH,
    TEST_SUBGROUP_DATA_PATH,
)
from config_optimisation import (
    RANDOM_STATE,
    IS_DUMMY_DATA,
    MIN_TRAIN_PER_CLASS,
    MIN_TEST_PER_CLASS,
    OPTIMISATION_OUTPUT_DIR,
    AT_RISK_RULES,
    SUBGROUP_VARS,
    GROUP_COUNT_COLS,
    CONFUSION_COUNT_COLS,
    METRIC_COLS,
)
from models_helpers import (
    get_model_specs,
    tune_model,
    evaluate_fitted_model,
    calculate_accuracy,
    safe_divide,
)



def load_model_data():
    

    train_data = pd.read_csv(TRAIN_DATA_PATH)
    test_data = pd.read_csv(TEST_DATA_PATH)

    age_band_cols = [
        col for col in train_data.columns
        if col.startswith("age_band_")
    ]

    drop_cols = ["patient_id", "hf_outcome"] + age_band_cols

    train_subgroups = pd.read_csv(TRAIN_SUBGROUP_DATA_PATH)
    test_subgroups = pd.read_csv(TEST_SUBGROUP_DATA_PATH)

    return {
        "X_train": train_data.drop(columns=drop_cols),
        "y_train": train_data["hf_outcome"],
        "X_test": test_data.drop(columns=drop_cols),
        "y_test": test_data["hf_outcome"],
        "train_ids": train_data["patient_id"],
        "test_ids": test_data["patient_id"],
        "train_subgroups": train_subgroups,
        "test_subgroups": test_subgroups,
    }


def make_output_dir(method):

    out_dir = os.path.join(OPTIMISATION_OUTPUT_DIR, method)
    os.makedirs(out_dir, exist_ok=True)

    return out_dir


# ----------------
# subgroups
# ----------------

def get_level_mask(values, level):
    """ True for patients with this level. Missing values are their own level """

    if pd.isna(level):
        return values.isna()

    return values == level


def get_subgroup_levels(test_subgroups, subgroup_vars=SUBGROUP_VARS,
                        train_subgroups=None):
    """ list of every subgroup level, with True/False masks marking the
    patients in it. train_subgroups is only needed when training a model
    per subgroup (04_1), so train_mask is None without it """

    groups = []

    for subgroup_var in subgroup_vars:

        # every value of this variable, in training and test patients
        if train_subgroups is None:
            all_values = test_subgroups[subgroup_var]
        else:
            all_values = pd.concat([
                train_subgroups[subgroup_var],
                test_subgroups[subgroup_var],
            ])

        levels = all_values.unique()

        for level_number, level in enumerate(levels):

            if pd.isna(level):
                level_label = "Missing"
            else:
                level_label = str(level)

            test_mask = get_level_mask(test_subgroups[subgroup_var], level)

            train_mask = None
            if train_subgroups is not None:
                train_mask = get_level_mask(train_subgroups[subgroup_var], level)

            groups.append({
                "subgroup_variable": subgroup_var,
                "subgroup_level": level_label,
                "level_number": level_number,
                "train_mask": train_mask,
                "test_mask": test_mask,
            })

    return groups


def get_rule_mask(values, levels):
    """ True where values match an AT_RISK_RULES entry: a list of levels,
    or {"min": value} for values >= min """

    if isinstance(levels, dict):
        return values >= levels["min"]

    return values.isin(levels)


def get_rule_label(levels): # if dict return >= min else return levels as string

    if isinstance(levels, dict):
        return f">={levels['min']}"

    return ", ".join(str(level) for level in levels)


def get_at_risk_groups(test_subgroups, train_subgroups):
    
    groups = []

    for level_number, (subgroup_var, levels) in enumerate(AT_RISK_RULES.items()):

        test_mask = get_rule_mask(test_subgroups[subgroup_var], levels)
        train_mask = get_rule_mask(train_subgroups[subgroup_var], levels)

        groups.append({
            "subgroup_variable": subgroup_var,
            "subgroup_level": get_rule_label(levels),
            "level_number": level_number,
            "train_mask": train_mask,
            "test_mask": test_mask,
        })

    return groups


def count_classes(y_train, y_test):

    counts = {}

    if y_train is not None:
        counts.update({
            "n_train": len(y_train),
            "train_events": int((y_train == 1).sum()),
            "train_nonevents": int((y_train == 0).sum()),
        })

    counts.update({
        "n_test": len(y_test),
        "test_events": int((y_test == 1).sum()),
        "test_nonevents": int((y_test == 0).sum()),
    })

    return counts


def get_skip_reason(counts):
    """ return why a subgroup should be skipped, or None """

    if "train_events" in counts and min(
        counts["train_events"], counts["train_nonevents"]
    ) < MIN_TRAIN_PER_CLASS:
        return "Too few training cases or non-cases"

    if min(
        counts["test_events"], counts["test_nonevents"]
    ) < MIN_TEST_PER_CLASS:
        return "Too few test cases or non-cases"

    return None



def get_at_risk_mask(subgroups, rules):
    """ True for patients in ANY of the at-risk groups defined in rules """

    mask = pd.Series(False, index=subgroups.index)

    for subgroup_var, levels in rules.items():
        mask = mask | get_rule_mask(subgroups[subgroup_var], levels)

    return mask



def fit_and_predict(X_train, y_train, X_test, y_test, test_ids, out_dir, cv,
                    X_threshold=None, y_threshold=None,
                    random_state=RANDOM_STATE):
    

    if X_threshold is None:
        X_threshold, y_threshold = X_train, y_train

    os.makedirs(out_dir, exist_ok=True)

    model_specs = get_model_specs(
        y_train=y_train,
        random_state=random_state,
    )

    prediction_df = pd.DataFrame({
        "patient_id": np.asarray(test_ids),
        "hf_outcome": np.asarray(y_test),
    })

    performance_rows = []

    for model_name, spec in model_specs.items():

        search = tune_model(
            model_name=model_name,
            model=spec["model"],
            params=spec["params"],
            search_type=spec["search_type"],
            X_train=X_train,
            y_train=y_train,
            cv=cv,
            scoring="roc_auc",
            n_iter=spec["n_iter"],
            random_state=random_state,
        )

        pd.DataFrame(search.cv_results_).to_csv(
            os.path.join(out_dir, f"cv_results_{model_name}.csv"),
            index=False,
        )

        test_pred, test_prob, performance, _ = evaluate_fitted_model(
            model=search.best_estimator_,
            X=X_threshold,
            y=y_threshold,
            X_val=X_test,
            y_val=y_test,
        )

        prediction_df[f"{model_name}_prob"] = test_prob
        prediction_df[f"{model_name}_pred"] = test_pred

        performance["model"] = model_name
        performance["best_cv_score"] = search.best_score_
        performance["best_params"] = str(search.best_params_)
        performance["threshold_method"] = "event_rate_train"

        performance_rows.append(performance)

        del search

    return pd.DataFrame(performance_rows), prediction_df



def get_model_names(prediction_df):
    """ model names from the <model>_prob columns """

    return [
        col.replace("_prob", "")
        for col in prediction_df.columns
        if col.endswith("_prob")
    ]


def evaluate_predictions(y_true, y_prob, y_pred):
    performance = calculate_accuracy(observed=y_true, predicted=y_pred)

    performance["auc"] = roc_auc_score(y_true, y_prob)
    performance["auc_pr"] = average_precision_score(y_true, y_prob)
    performance["brier"] = brier_score_loss(y_true, y_prob)
    performance["mean_predicted_risk"] = np.mean(y_prob)

    return performance


def evaluate_in_subgroups(prediction_df, test_subgroups,
                          subgroup_vars=SUBGROUP_VARS):

    eval_data = prediction_df.merge(
        test_subgroups,
        on=["patient_id", "hf_outcome"],
        how="left",
    )

    rows = []

    for model_name in get_model_names(prediction_df):

        for group in get_subgroup_levels(eval_data, subgroup_vars):

            df_sub = eval_data.loc[group["test_mask"]]

            y_true = df_sub["hf_outcome"]
            y_prob = df_sub[f"{model_name}_prob"]
            y_pred = df_sub[f"{model_name}_pred"].astype(int)

            counts = count_classes(y_train=None, y_test=y_true)

            row = {
                "model": model_name,
                "subgroup_variable": group["subgroup_variable"],
                "subgroup_level": group["subgroup_level"],
                **counts,
                "event_rate": y_true.mean(),
            }

            confusion = calculate_accuracy(observed=y_true, predicted=y_pred)
            row.update({col: confusion[col] for col in CONFUSION_COUNT_COLS})

            reason = get_skip_reason(counts)

            if reason is None:
                row.update(evaluate_predictions(y_true, y_prob, y_pred))
            else:
                row.update({col: np.nan for col in METRIC_COLS})

            row["skip_reason"] = reason

            rows.append(row)

    return pd.DataFrame(rows)




def recalculate_rates(out):
    """ work out the rates again from the rounded counts, so the exact
    counts cannot be worked back from the rates (e.g. 1 case in 11 patients
    from an exact rate of 0.0909) """

    # tables without a confusion matrix (skipped subgroups) have no rates
    if "true_positives" not in out.columns:
        return out

    for row_number in out.index:

        # rounded counts for this row
        tp = out.loc[row_number, "true_positives"]
        fp = out.loc[row_number, "false_positives"]
        tn = out.loc[row_number, "true_negatives"]
        fn = out.loc[row_number, "false_negatives"]
        n_test = out.loc[row_number, "n_test"]
        test_events = out.loc[row_number, "test_events"]
        test_nonevents = out.loc[row_number, "test_nonevents"]

        # same rates as calculate_accuracy, from the rounded counts
        total = tp + fp + tn + fn
        precision = safe_divide(tp, tp + fp)
        recall = safe_divide(tp, tp + fn)
        specificity = safe_divide(tn, tn + fp)

        if np.isnan(precision) or np.isnan(recall) or (precision + recall == 0):
            f1 = np.nan
        else:
            f1 = 2 * precision * recall / (precision + recall)

        new_rates = {
            "event_rate": safe_divide(test_events, n_test),
            "observed_event_rate": safe_divide(test_events, n_test),
            "observed_positive_rate": safe_divide(test_events, n_test),
            "observed_negative_rate": safe_divide(test_nonevents, n_test),
            "predicted_positive_rate": safe_divide(tp + fp, total),
            "predicted_negative_rate": safe_divide(tn + fn, total),
            "accuracy": safe_divide(tp + tn, total),
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "sensitivity": recall,
            "specificity": specificity,
            "positive_likelihood": safe_divide(recall, 1 - specificity),
            "negative_likelihood": safe_divide(1 - recall, specificity),
            "false_positive_rate": 1 - specificity,
            "false_negative_rate": 1 - recall,
            "true_positive_rate": recall,
            "true_negative_rate": specificity,
            "positive_predictive_value": precision,
            "negative_predictive_value": safe_divide(tn, tn + fn),
        }

        for col, value in new_rates.items():

            # only replace rates that are in this table and were filled in:
            # skipped subgroups are left empty on purpose
            if col in out.columns and pd.notna(out.loc[row_number, col]):
                out.loc[row_number, col] = value

    return out


def save_with_sdc(df, path, count_cols=GROUP_COUNT_COLS + CONFUSION_COUNT_COLS):

    out = df.copy()

    if not IS_DUMMY_DATA:
        out = apply_sdc_to_counts(out, count_cols, threshold=DISCLOSURE_THRESHOLD)
        out = recalculate_rates(out)

    out.to_csv(path, index=False)

    return out


def plot_confusion_matrices(performance_df, out_dir, method,
                            group_cols=("subgroup_variable", "subgroup_level")):
    

    if not IS_DUMMY_DATA:
        return

    cm_dir = os.path.join(out_dir, "confusion_matrices")
    os.makedirs(cm_dir, exist_ok=True)

    for (subgroup_var, subgroup_level), df_group in performance_df.groupby(
        list(group_cols)
    ):

        fig, axes = plt.subplots(
            1,
            len(df_group),
            figsize=(5 * len(df_group), 4),
            squeeze=False,
        )

        for ax, (_, row) in zip(axes[0], df_group.iterrows()):

            cm = np.array([
                [row["true_negatives"], row["false_positives"]],
                [row["false_negatives"], row["true_positives"]],
            ])

            ConfusionMatrixDisplay(
                confusion_matrix=cm,
                display_labels=["0", "1"],
            ).plot(ax=ax, colorbar=False)

            ax.set_title(row["model"])

        fig.suptitle(f"{subgroup_var}: {subgroup_level}", fontsize=14)
        plt.tight_layout()

        safe_var = str(subgroup_var).replace(" ", "_").replace("/", "_")
        safe_level = str(subgroup_level).replace(" ", "_").replace("/", "_")

        fig.savefig(
            os.path.join(cm_dir, f"cm_{method}_{safe_var}_{safe_level}.png"),
            dpi=200,
            bbox_inches="tight",
        )

        plt.show()
        plt.close(fig)

