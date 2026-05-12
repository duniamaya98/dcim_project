import numpy as np


def calculate_drift_score(input_array, baseline_mean, baseline_std):
    """
    Z-score based drift calculation
    """

    baseline_mean = np.array(baseline_mean)
    baseline_std = np.array(baseline_std)

    # Prevent division by zero
    baseline_std = np.where(baseline_std == 0, 1e-6, baseline_std)

    z_scores = np.abs((input_array - baseline_mean) / baseline_std)

    drift_score = float(np.mean(z_scores))

    return drift_score, z_scores.tolist()


def classify_drift(drift_score):
    """
    Simple severity classification
    """

    if drift_score < 1:
        return "stable"
    elif drift_score < 2:
        return "mild_drift"
    elif drift_score < 3:
        return "moderate_drift"
    else:
        return "severe_drift"
