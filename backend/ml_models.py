"""
Machine learning models for Sentinel-Net repository reliability scoring.
Includes training dataset generation, stacking ensemble training, and
confidence/uncertainty-aware inference.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import json
import math
import pickle

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor, GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import StackingRegressor


CURRENT_DIR = Path(__file__).resolve().parent
ARTIFACT_DIR = CURRENT_DIR / "models"
DATA_DIR = CURRENT_DIR / "data"
MODEL_ARTIFACT = ARTIFACT_DIR / "risk_model.pkl"
STATUS_ARTIFACT = ARTIFACT_DIR / "training_status.json"
DATASET_ARTIFACT = DATA_DIR / "repository_risk_training.csv"
MODEL_VERSION = "1.0.0"


@dataclass
class TrainingStatus:
    trained: bool
    model_name: str
    model_version: str
    sample_count: int
    feature_count: int
    trained_at: str
    metrics: Dict[str, float]
    dataset_path: str


@dataclass
class RiskPrediction:
    predicted_risk_score: float
    confidence: float
    uncertainty: float
    ml_risk_score: float
    blended_risk_score: float
    nlp_signal_score: float
    contributing_factors: Dict[str, float]
    model_name: str
    model_version: str
    timestamp: str


class RiskScorePredictorML:
    """Stacking ensemble regressor for repository reliability risk."""

    def __init__(self) -> None:
        ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        self.feature_columns: List[str] = [
            "commits_30d",
            "contributors_30d",
            "open_issues",
            "closed_issues_30d",
            "open_prs",
            "avg_commit_frequency",
            "code_churn_rate",
            "bug_fix_ratio",
            "urgent_signal_ratio",
            "negative_sentiment_ratio",
            "test_coverage",
            "ci_failures_rate",
            "mean_pr_cycle_time_hours",
            "release_stability_index",
            "issue_to_commit_ratio",
            "bus_factor_inverse",
            "developer_load_index",
            "commit_volatility",
        ]
        self.pipeline: Pipeline | None = None
        self.status = TrainingStatus(
            trained=False,
            model_name="StackingRegressor",
            model_version=MODEL_VERSION,
            sample_count=0,
            feature_count=len(self.feature_columns),
            trained_at="",
            metrics={},
            dataset_path=str(DATASET_ARTIFACT),
        )

        self._load_or_train()

    def _load_or_train(self) -> None:
        if MODEL_ARTIFACT.exists() and STATUS_ARTIFACT.exists():
            try:
                with MODEL_ARTIFACT.open("rb") as f:
                    payload = pickle.load(f)
                with STATUS_ARTIFACT.open("r", encoding="utf-8") as f:
                    status_data = json.load(f)

                self.pipeline = payload["pipeline"]
                self.feature_columns = payload["feature_columns"]
                self.status = TrainingStatus(**status_data)
                return
            except Exception:
                # If artifact is corrupt or stale, retrain.
                pass

        self.train_model()

    def _generate_training_dataset(self, sample_count: int = 1400, seed: int = 42) -> pd.DataFrame:
        rng = np.random.default_rng(seed)

        commits_30d = rng.integers(0, 320, sample_count)
        contributors_30d = rng.integers(1, 55, sample_count)
        open_issues = rng.integers(0, 700, sample_count)
        closed_issues_30d = rng.integers(0, 400, sample_count)
        open_prs = rng.integers(0, 180, sample_count)

        avg_commit_frequency = commits_30d / 30.0 + rng.normal(0, 0.7, sample_count)
        avg_commit_frequency = np.clip(avg_commit_frequency, 0, None)

        code_churn_rate = np.clip(rng.beta(2.0, 5.0, sample_count), 0.01, 1.0)
        bug_fix_ratio = np.clip(rng.beta(2.2, 3.2, sample_count), 0.0, 1.0)
        urgent_signal_ratio = np.clip(rng.beta(1.6, 5.8, sample_count), 0.0, 1.0)
        negative_sentiment_ratio = np.clip(rng.beta(2.0, 4.2, sample_count), 0.0, 1.0)

        test_coverage = np.clip(rng.normal(71, 16, sample_count), 5, 100)
        ci_failures_rate = np.clip(rng.beta(1.8, 9.2, sample_count), 0.0, 1.0)
        mean_pr_cycle_time_hours = np.clip(rng.normal(19, 9.5, sample_count), 1, 120)
        release_stability_index = np.clip(rng.normal(0.68, 0.2, sample_count), 0.0, 1.0)

        issue_to_commit_ratio = open_issues / np.maximum(commits_30d, 1)
        bus_factor_inverse = 1 / np.sqrt(np.maximum(contributors_30d, 1))
        developer_load_index = (open_issues + open_prs) / np.maximum(contributors_30d, 1)
        commit_volatility = np.clip(rng.beta(2.5, 4.8, sample_count), 0.0, 1.0)

        # Synthetic target that encodes nonlinear effects + interactions.
        raw_target = (
            10
            + 9.5 * np.log1p(issue_to_commit_ratio)
            + 18.0 * urgent_signal_ratio
            + 14.5 * negative_sentiment_ratio
            + 12.0 * ci_failures_rate
            + 8.0 * code_churn_rate
            + 6.2 * bug_fix_ratio
            + 0.055 * developer_load_index
            + 7.0 * commit_volatility
            + 5.3 * bus_factor_inverse
            + 0.035 * mean_pr_cycle_time_hours
            - 0.26 * test_coverage
            - 11.5 * release_stability_index
            + np.where(commits_30d == 0, 15.0, 0.0)
            + np.where(open_issues > 250, 8.0, 0.0)
            + rng.normal(0, 3.2, sample_count)
        )

        risk_score = np.clip(raw_target, 0, 100)

        dataset = pd.DataFrame(
            {
                "commits_30d": commits_30d,
                "contributors_30d": contributors_30d,
                "open_issues": open_issues,
                "closed_issues_30d": closed_issues_30d,
                "open_prs": open_prs,
                "avg_commit_frequency": avg_commit_frequency,
                "code_churn_rate": code_churn_rate,
                "bug_fix_ratio": bug_fix_ratio,
                "urgent_signal_ratio": urgent_signal_ratio,
                "negative_sentiment_ratio": negative_sentiment_ratio,
                "test_coverage": test_coverage,
                "ci_failures_rate": ci_failures_rate,
                "mean_pr_cycle_time_hours": mean_pr_cycle_time_hours,
                "release_stability_index": release_stability_index,
                "issue_to_commit_ratio": issue_to_commit_ratio,
                "bus_factor_inverse": bus_factor_inverse,
                "developer_load_index": developer_load_index,
                "commit_volatility": commit_volatility,
                "target_risk": risk_score,
            }
        )

        dataset.to_csv(DATASET_ARTIFACT, index=False)
        return dataset

    def train_model(self) -> TrainingStatus:
        dataset = self._generate_training_dataset()
        x = dataset[self.feature_columns]
        y = dataset["target_risk"]

        x_train, x_test, y_train, y_test = train_test_split(
            x,
            y,
            test_size=0.2,
            random_state=42,
        )

        estimators: List[Tuple[str, Any]] = [
            (
                "rf",
                RandomForestRegressor(
                    n_estimators=260,
                    max_depth=15,
                    min_samples_leaf=2,
                    random_state=42,
                    n_jobs=-1,
                ),
            ),
            (
                "gbr",
                GradientBoostingRegressor(
                    n_estimators=250,
                    learning_rate=0.05,
                    max_depth=3,
                    random_state=42,
                ),
            ),
            (
                "etr",
                ExtraTreesRegressor(
                    n_estimators=240,
                    max_depth=14,
                    min_samples_leaf=2,
                    random_state=42,
                    n_jobs=-1,
                ),
            ),
        ]

        model = StackingRegressor(
            estimators=estimators,
            final_estimator=Ridge(alpha=1.0),
            cv=5,
            n_jobs=-1,
        )

        self.pipeline = Pipeline(
            [
                ("scaler", StandardScaler()),
                ("model", model),
            ]
        )
        self.pipeline.fit(x_train, y_train)

        y_pred = self.pipeline.predict(x_test)
        rmse = float(math.sqrt(mean_squared_error(y_test, y_pred)))
        mae = float(mean_absolute_error(y_test, y_pred))
        r2 = float(r2_score(y_test, y_pred))

        metrics = {
            "rmse": round(rmse, 4),
            "mae": round(mae, 4),
            "r2": round(r2, 4),
        }

        self.status = TrainingStatus(
            trained=True,
            model_name="StackingRegressor(RandomForest, GradientBoosting, ExtraTrees -> Ridge)",
            model_version=MODEL_VERSION,
            sample_count=int(dataset.shape[0]),
            feature_count=len(self.feature_columns),
            trained_at=datetime.utcnow().isoformat() + "Z",
            metrics=metrics,
            dataset_path=str(DATASET_ARTIFACT),
        )

        with MODEL_ARTIFACT.open("wb") as f:
            pickle.dump(
                {
                    "pipeline": self.pipeline,
                    "feature_columns": self.feature_columns,
                },
                f,
            )

        with STATUS_ARTIFACT.open("w", encoding="utf-8") as f:
            json.dump(asdict(self.status), f, indent=2)

        return self.status

    def get_training_status(self) -> Dict[str, Any]:
        return asdict(self.status)

    def _to_feature_vector(self, feature_payload: Dict[str, float]) -> pd.DataFrame:
        row = {col: float(feature_payload.get(col, 0.0)) for col in self.feature_columns}
        # Ensure engineered fields are always coherent if omitted.
        if row["issue_to_commit_ratio"] == 0:
            row["issue_to_commit_ratio"] = row["open_issues"] / max(row["commits_30d"], 1)
        if row["bus_factor_inverse"] == 0:
            row["bus_factor_inverse"] = 1 / math.sqrt(max(row["contributors_30d"], 1.0))
        if row["developer_load_index"] == 0:
            row["developer_load_index"] = (row["open_issues"] + row["open_prs"]) / max(row["contributors_30d"], 1)
        return pd.DataFrame([row], columns=self.feature_columns)

    def _compute_factor_importance(
        self,
        feature_row: pd.Series,
        model_risk: float,
        nlp_signal_score: float,
    ) -> Dict[str, float]:
        # Human-readable weighted factors; keeps output deterministic.
        weights = {
            "issue_pressure": 0.24,
            "delivery_risk": 0.18,
            "code_stability": 0.17,
            "quality_guardrails": 0.16,
            "team_dynamics": 0.13,
            "nlp_signal": 0.12,
        }

        issue_pressure = min(1.0, math.log1p(feature_row["issue_to_commit_ratio"]) / 2.2)
        delivery_risk = min(1.0, (feature_row["open_prs"] / 120) + (feature_row["mean_pr_cycle_time_hours"] / 180))
        code_stability = min(1.0, feature_row["code_churn_rate"] * 0.65 + feature_row["commit_volatility"] * 0.35)
        quality_guardrails = min(1.0, (1 - feature_row["test_coverage"] / 100) * 0.65 + feature_row["ci_failures_rate"] * 0.35)
        team_dynamics = min(1.0, feature_row["developer_load_index"] / 100 + feature_row["bus_factor_inverse"])
        nlp_signal = min(1.0, nlp_signal_score / 100)

        values = {
            "issue_pressure": issue_pressure,
            "delivery_risk": delivery_risk,
            "code_stability": code_stability,
            "quality_guardrails": quality_guardrails,
            "team_dynamics": team_dynamics,
            "nlp_signal": nlp_signal,
        }

        weighted = {k: round(v * weights[k], 4) for k, v in values.items()}
        total = sum(weighted.values()) or 1.0
        normalized = {k: round((v / total), 4) for k, v in weighted.items()}
        normalized["model_risk_norm"] = round(model_risk / 100, 4)
        return normalized

    def predict(
        self,
        feature_payload: Dict[str, float],
        nlp_signal_score: float,
        blend_alpha: float = 0.8,
    ) -> RiskPrediction:
        if self.pipeline is None:
            self.train_model()

        features = self._to_feature_vector(feature_payload)
        model = self.pipeline.named_steps["model"]

        base_array = features.values
        base_preds = []
        for est in model.estimators_:
            base_preds.append(float(est.predict(base_array)[0]))

        ml_risk = float(self.pipeline.predict(features)[0])
        ml_risk = float(np.clip(ml_risk, 0.0, 100.0))

        # Ensemble spread + model RMSE as uncertainty proxy.
        spread = float(np.std(base_preds))
        rmse = float(self.status.metrics.get("rmse", 6.0))
        uncertainty = float(np.clip((spread * 0.6 + rmse * 0.4) / 100, 0.01, 0.6))
        confidence = float(np.clip(1.0 - uncertainty, 0.35, 0.99))

        blended = float(np.clip((blend_alpha * ml_risk) + ((1 - blend_alpha) * nlp_signal_score), 0.0, 100.0))
        factors = self._compute_factor_importance(features.iloc[0], ml_risk, nlp_signal_score)

        return RiskPrediction(
            predicted_risk_score=round(blended, 2),
            confidence=round(confidence, 4),
            uncertainty=round(uncertainty, 4),
            ml_risk_score=round(ml_risk, 2),
            blended_risk_score=round(blended, 2),
            nlp_signal_score=round(float(nlp_signal_score), 2),
            contributing_factors=factors,
            model_name=self.status.model_name,
            model_version=self.status.model_version,
            timestamp=datetime.utcnow().isoformat() + "Z",
        )


class AnomalyDetector:
    """Simple anomaly detector over temporal risk signals."""

    def detect_anomalies(
        self,
        temporal_data: List[Dict[str, Any]],
    ) -> Tuple[bool, float, List[Dict[str, Any]]]:
        if len(temporal_data) < 3:
            return False, 0.0, []

        bug_growth = np.array([float(x.get("bugGrowth", 0)) for x in temporal_data], dtype=float)
        dev_irregularity = np.array([float(x.get("devIrregularity", 0)) for x in temporal_data], dtype=float)
        combined = 0.6 * bug_growth + 0.4 * dev_irregularity

        mean = float(np.mean(combined))
        std = float(np.std(combined))
        threshold = mean + max(1.5 * std, 8.0)

        anomalies: List[Dict[str, Any]] = []
        for idx, value in enumerate(combined):
            if value > threshold:
                severity = float(np.clip((value - threshold) / max(threshold, 1), 0.05, 1.0))
                anomalies.append(
                    {
                        "index": idx,
                        "timestamp": temporal_data[idx].get("timestamp"),
                        "severity": round(severity, 4),
                        "bugGrowth": bug_growth[idx],
                        "devIrregularity": dev_irregularity[idx],
                    }
                )

        if not anomalies:
            return False, 0.0, []

        return True, round(max(item["severity"] for item in anomalies), 4), anomalies


_global_predictor: RiskScorePredictorML | None = None
_global_anomaly_detector: AnomalyDetector | None = None


def get_risk_predictor() -> RiskScorePredictorML:
    global _global_predictor
    if _global_predictor is None:
        _global_predictor = RiskScorePredictorML()
    return _global_predictor


def get_anomaly_detector() -> AnomalyDetector:
    global _global_anomaly_detector
    if _global_anomaly_detector is None:
        _global_anomaly_detector = AnomalyDetector()
    return _global_anomaly_detector
