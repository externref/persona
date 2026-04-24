# from persona.types import BiometricProfile
import numpy as np
from sklearn.ensemble import IsolationForest


def z_score_anomaly_detection(db_profile, received_profile, feature_keys=None, anomaly_threshold=2.5):
    """
    Compare profiles using Z-score for anomaly detection.

    Args:
        db_profile (dict or BiometricProfile): Profile from DB.
        received_profile (dict or BiometricProfile): Profile from request.
        feature_keys (list, optional): Which features to compare. If None, use intersection.
        anomaly_threshold (float): Z-score above which a feature is considered an anomaly.

    Returns:
        dict: { 'anomaly': bool, 'score': float, 'details': dict }
    """
    db_features = (
        db_profile["features"] if isinstance(db_profile, dict) else db_profile.features
    )
    rec_features = (
        received_profile["features"]
        if isinstance(received_profile, dict)
        else received_profile.features
    )

    if feature_keys is None:
        # Use features present in both, excluding those with zero variance in the db
        feature_keys = [
            k
            for k, v in db_features.items()
            if k in rec_features and v.get("std_dev", 0) > 1e-9
        ]

    if not feature_keys:
        return {
            "anomaly": True,
            "score": 1.0,
            "details": {"error": "No comparable features with variance found."},
        }

    details = {}
    total_z_score = 0
    total_weight = 0

    for k in feature_keys:
        db_mean = db_features[k].get("mean", 0.0)
        db_std = db_features[k].get("std_dev", 0.0)
        rec_mean = rec_features[k].get("mean", 0.0)
        weight = db_features[k].get("weight", 1.0)

        # Calculate Z-score for the received mean against the database distribution
        z_score = abs(rec_mean - db_mean) / db_std if db_std > 1e-9 else 0.0

        details[k] = {
            "db_mean": db_mean,
            "db_std": db_std,
            "rec_mean": rec_mean,
            "z_score": z_score,
            "is_anomaly": z_score > anomaly_threshold,
        }

        total_z_score += z_score * weight
        total_weight += weight

    # Calculate the weighted average Z-score
    average_z_score = total_z_score / total_weight if total_weight > 0 else 0.0

    # Determine overall anomaly status
    # Anomaly if the average score is high or if any single important feature is an anomaly
    is_anomaly = average_z_score > anomaly_threshold or any(
        d["is_anomaly"] for d in details.values()
    )

    # Normalize the score to a 0-1 range for easier interpretation
    # Sigmoid-like function to map Z-score to a probability-like score
    final_score = 1 / (1 + np.exp(-2 * (average_z_score - anomaly_threshold)))

    return {
        "anomaly": np.bool_(is_anomaly),
        "score": float(final_score),
        "details": details,
    }

# The original function is replaced by the more appropriate Z-score method.
# The name is kept for compatibility with the calling code in main.py
compare_payloads_isolation_forest = z_score_anomaly_detection
