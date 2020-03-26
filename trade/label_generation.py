from __future__ import annotations  # Eliminates problem with type annotations like list[int]
import os
from datetime import datetime, timezone, timedelta
from typing import Union
import json

import numpy as np
import pandas as pd

from trade.utils import *

"""
Label generation.
(True) labels are features computed from future data but stored as properties of the current row (in contrast to normal features which are computed from past data).
"""

def generate_labels_thresholds(df, horizon=60):
    """
    Generate (compute) a number of labels similar to other derived features but using future data.
    This function is used only in training.
    For prediction, the labels are computed by the models (not from future data which is absent).

    We use the following conventions and dimensions for generating binary labels:
    - Threshold is used to compare all values of some parameter, for example, 0.5 or 2.0 (sign is determined from the context)
    - Greater or less than the threshold. Note that the threshold has a sign which however is determined from the context
    - High or low column to compare with the threshold. Note that relative deviations from the close are used.
      Hence, high is always positive and low is always negative.
    - horizon which determines the future window used to compute all or one
    Thus, a general label is computed via the condition: [all or one] [relative high or low] [>= or <=] threshold
    However, we do not need all combinations of parameters but rather only some of them which are grouped as follows:
    - high >= large_threshold - at least one higher than threshold: 0.5, 1.0, 1.5, 2.0, 2.5
    - high <= small_threshold - all lower than threshold: 0.1, 0.2, 0.3, 0.4
    - low >= -small_threshold - all higher than threshold: 0.1, 0.2, 0.3, 0.4
    - low <= -large_threshold - at least one lower than (negative) threshold: 0.5, 1.0, 1.5, 2.0, 2.5
    Accordingly, we encode the labels as follows (60 is horizon):
    - high_60_xx (xx is threshold): for big xx - high_xx means one is larger, for small xx - all are less
    - low_60_xx (xx is threshold): for big xx - low_xx means one is larger, for small xx - all are less
    """
    labels = []
    to_drop = []

    # Max high
    to_drop += add_future_aggregations(df, "high", np.max, horizon, suffix='_max', rel_column_name="close", rel_factor=100.0)

    # Max high crosses (is over) the threshold
    labels += add_threshold_feature(df, "high_max_60", thresholds=[1.0, 1.5, 2.0, 2.5], out_names=["high_60_10", "high_60_15", "high_60_20", "high_60_25"])
    # Max high does not cross (is under) the threshold
    labels += add_threshold_feature(df, "high_max_60", thresholds=[0.1, 0.2, 0.3, 0.4], out_names=["high_60_01", "high_60_02", "high_60_03", "high_60_04"])

    # Min low
    to_drop += add_future_aggregations(df, "low", np.min, horizon, suffix='_min', rel_column_name="close", rel_factor=100.0)

    # Min low does not cross (is over) the negative threshold
    labels += add_threshold_feature(df, "low_min_60", thresholds=[-0.1, -0.2, -0.3, -0.4], out_names=["low_60_01", "low_60_02", "low_60_03", "low_60_04"])
    # Min low crosses (is under) the negative threshold
    labels += add_threshold_feature(df, "low_min_60", thresholds=[-1.0, -1.5, -2.0, -2.5], out_names=["low_60_10", "low_60_15", "low_60_20", "low_60_25"])

    df.drop(columns=to_drop, inplace=True)

    return labels

def generate_labels_sim(df, horizon):
    labels = []

    # Max high
    add_future_aggregations(df, "high", np.max, horizon, suffix='_max', rel_column_name="close", rel_factor=100.0)

    # Max high crosses (is over) the threshold
    labels += add_threshold_feature(df, "high_max_60", thresholds=[2.0], out_names=["high_60_20"])
    # Max high does not cross (is under) the threshold
    labels += add_threshold_feature(df, "high_max_60", thresholds=[0.2], out_names=["high_60_02"])

    # Min low
    add_future_aggregations(df, "low", np.min, horizon, suffix='_min', rel_column_name="close", rel_factor=100.0)

    # Min low does not cross (is over) the negative threshold
    labels += add_threshold_feature(df, "low_min_60", thresholds=[-0.2], out_names=["low_60_02"])
    # Min low crosses (is under) the negative threshold
    labels += add_threshold_feature(df, "low_min_60", thresholds=[-2.0], out_names=["low_60_20"])

    return labels

def generate_labels_regressor(df, horizon):
    labels = []

    # Max high relative to close in percent
    labels += add_future_aggregations(df, "high", np.max, horizon, suffix='_max', rel_column_name="close", rel_factor=100.0)
    # "high_max_60"

    # Min low relative to close in percent (negative values)
    labels += add_future_aggregations(df, "low", np.min, horizon, suffix='_min', rel_column_name="close", rel_factor=100.0)
    # "low_min_60"

    return labels

if __name__ == "__main__":
    pass