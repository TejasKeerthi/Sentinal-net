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
MODEL_VERSION = "2.0.0"


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
    """Niche dual-head fusion model for repository reliability risk."""

    def __init__(self) -> None:
        ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        self.default_feature_columns: List[str] = [
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
            "issue_momentum",
            "signal_entropy",
            "release_friction_index",
            "socio_technical_strain",
            "remediation_latency",
            "collaboration_imbalance",
        ]
        self.feature_columns: List[str] = list(self.default_feature_columns)
        # Keep self.pipeline for compatibility with older code paths.
        self.pipeline: Pipeline | None = None
        self.primary_pipeline: Pipeline | None = None
        self.stress_pipeline: Pipeline | None = None
        self.status = TrainingStatus(
            trained=False,
            model_name="DualHeadAdaptiveRiskFusion",
            model_version=MODEL_VERSION,
            sample_count=0,
            feature_count=len(self.feature_columns),
            trained_at="",
            metrics={},
            dataset_path=str(DATASET_ARTIFACT),
        )

        self._load_or_train()

    def _load_or_train(self) -> None:
        needs_train = True
        if MODEL_ARTIFACT.exists() and STATUS_ARTIFACT.exists():
            try:
                with MODEL_ARTIFACT.open("rb") as f:
                    payload = pickle.load(f)
                with STATUS_ARTIFACT.open("r", encoding="utf-8") as f:
                    status_data = json.load(f)

                self.primary_pipeline = payload.get("primary_pipeline") or payload.get("pipeline")
                self.stress_pipeline = payload.get("stress_pipeline")
                self.pipeline = self.primary_pipeline
                self.feature_columns = payload.get("feature_columns", self.feature_columns)
                self.status = TrainingStatus(**status_data)

                needs_train = (
                    self.status.model_version != MODEL_VERSION
                    or self.status.feature_count != len(self.feature_columns)
                    or self.primary_pipeline is None
                    or self.stress_pipeline is None
                )
            except Exception:
                # If artifact is corrupt or stale, retrain.
                needs_train = True

        if needs_train:
            self.feature_columns = list(self.default_feature_columns)
            self.train_model()
    @staticmethod
    def _derive_specialty_features(row: Dict[str, float]) -> Dict[str, float]:
        issue_momentum = (row["open_issues"] - row["closed_issues_30d"]) / max(
            row["open_issues"] + row["closed_issues_30d"],
            1.0,
        )

        urgent = float(np.clip(row["urgent_signal_ratio"], 0.0001, 0.9999))
        negative = float(np.clip(row["negative_sentiment_ratio"], 0.0001, 0.9999))
        urgent_entropy = -(urgent * math.log(urgent) + (1 - urgent) * math.log(1 - urgent)) / math.log(2)
        negative_entropy = -(negative * math.log(negative) + (1 - negative) * math.log(1 - negative)) / math.log(2)
        signal_entropy = float(np.clip((urgent_entropy + negative_entropy) / 2.0, 0.0, 1.0))

        release_friction_index = (
            row["ci_failures_rate"] * (row["mean_pr_cycle_time_hours"] / 36.0) * (1.0 + (1.0 - row["release_stability_index"]))
        )
        socio_technical_strain = row["developer_load_index"] * (1 + row["negative_sentiment_ratio"]) * row["bus_factor_inverse"]
        remediation_latency = (1 - row["bug_fix_ratio"]) * row["issue_to_commit_ratio"] * 10.0
        collaboration_imbalance = row["commit_volatility"] * row["bus_factor_inverse"] * (1 + row["urgent_signal_ratio"])

        return {
            "issue_momentum": float(np.clip(issue_momentum, -1.0, 1.0)),
            "signal_entropy": signal_entropy,
            "release_friction_index": float(np.clip(release_friction_index, 0.0, 8.0)),
            "socio_technical_strain": float(np.clip(socio_technical_strain, 0.0, 300.0)),
            "remediation_latency": float(np.clip(remediation_latency, 0.0, 300.0)),
            "collaboration_imbalance": float(np.clip(collaboration_imbalance, 0.0, 2.0)),
        }


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

        specialty = []
        for i in range(sample_count):
            base = {
                "open_issues": float(open_issues[i]),
                "closed_issues_30d": float(closed_issues_30d[i]),
                "urgent_signal_ratio": float(urgent_signal_ratio[i]),
                "negative_sentiment_ratio": float(negative_sentiment_ratio[i]),
                "ci_failures_rate": float(ci_failures_rate[i]),
                "mean_pr_cycle_time_hours": float(mean_pr_cycle_time_hours[i]),
                "release_stability_index": float(release_stability_index[i]),
                "developer_load_index": float(developer_load_index[i]),
                "bus_factor_inverse": float(bus_factor_inverse[i]),
                "bug_fix_ratio": float(bug_fix_ratio[i]),
                "issue_to_commit_ratio": float(issue_to_commit_ratio[i]),
                "commit_volatility": float(commit_volatility[i]),
            }
            specialty.append(self._derive_specialty_features(base))

        issue_momentum = np.array([x["issue_momentum"] for x in specialty])
        signal_entropy = np.array([x["signal_entropy"] for x in specialty])
        release_friction_index = np.array([x["release_friction_index"] for x in specialty])
        socio_technical_strain = np.array([x["socio_technical_strain"] for x in specialty])
        remediation_latency = np.array([x["remediation_latency"] for x in specialty])
        collaboration_imbalance = np.array([x["collaboration_imbalance"] for x in specialty])

        # Synthetic target that encodes nonlinear effects + niche reliability signatures.
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
            + 2.8 * signal_entropy
            + 1.2 * release_friction_index
            + 0.04 * socio_technical_strain
            + 0.06 * remediation_latency
            + 9.0 * collaboration_imbalance
            + np.where(issue_momentum > 0.35, 7.5, 0.0)
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
                "issue_momentum": issue_momentum,
                "signal_entropy": signal_entropy,
                "release_friction_index": release_friction_index,
                "socio_technical_strain": socio_technical_strain,
                "remediation_latency": remediation_latency,
                "collaboration_imbalance": collaboration_imbalance,
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

        self.primary_pipeline = Pipeline(
            [
                ("scaler", StandardScaler()),
                ("model", model),
            ]
        )
        self.primary_pipeline.fit(x_train, y_train)

        stress_columns = [
            "issue_momentum",
            "signal_entropy",
            "release_friction_index",
            "socio_technical_strain",
            "remediation_latency",
            "collaboration_imbalance",
            "urgent_signal_ratio",
            "negative_sentiment_ratio",
            "issue_to_commit_ratio",
            "developer_load_index",
            "ci_failures_rate",
            "mean_pr_cycle_time_hours",
        ]

        self.stress_pipeline = Pipeline(
            [
                ("scaler", StandardScaler()),
                (
                    "model",
                    GradientBoostingRegressor(
                        n_estimators=280,
                        learning_rate=0.045,
                        max_depth=3,
                        random_state=42,
                    ),
                ),
            ]
        )
        self.stress_pipeline.fit(x_train[stress_columns], y_train)

        self.pipeline = self.primary_pipeline

        y_backbone = self.primary_pipeline.predict(x_test)
        y_stress = self.stress_pipeline.predict(x_test[stress_columns])
        gate = np.clip(
            0.25
            + (0.32 * (x_test["signal_entropy"] / np.maximum(x_test["signal_entropy"].max(), 1e-4)))
            + (0.28 * np.tanh(x_test["release_friction_index"] / 2.5))
            + (0.15 * np.tanh(x_test["socio_technical_strain"] / 20.0)),
            0.2,
            0.85,
        )

        y_pred = ((1 - gate) * y_backbone) + (gate * y_stress)
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
            model_name="Dual-Head Adaptive Risk Fusion (Stacking + StressRegressor)",
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
                    "primary_pipeline": self.primary_pipeline,
                    "stress_pipeline": self.stress_pipeline,
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
        base_columns = [
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
        row = {col: float(feature_payload.get(col, 0.0)) for col in base_columns}
        # Ensure engineered fields are always coherent if omitted.
        if row["issue_to_commit_ratio"] == 0:
            row["issue_to_commit_ratio"] = row["open_issues"] / max(row["commits_30d"], 1)
        if row["bus_factor_inverse"] == 0:
            row["bus_factor_inverse"] = 1 / math.sqrt(max(row["contributors_30d"], 1.0))
        if row["developer_load_index"] == 0:
            row["developer_load_index"] = (row["open_issues"] + row["open_prs"]) / max(row["contributors_30d"], 1)

        row.update(self._derive_specialty_features(row))
        return pd.DataFrame([row], columns=self.feature_columns)

    def _compute_factor_importance(
        self,
        feature_row: pd.Series,
        model_risk: float,
        nlp_signal_score: float,
    ) -> Dict[str, float]:
        # Human-readable weighted factors; keeps output deterministic.
        weights = {
            "issue_pressure": 0.2,
            "delivery_risk": 0.14,
            "code_stability": 0.13,
            "quality_guardrails": 0.13,
            "team_dynamics": 0.12,
            "system_fragility_signature": 0.14,
            "coordination_debt_signature": 0.08,
            "nlp_signal": 0.06,
        }

        issue_pressure = min(1.0, math.log1p(feature_row["issue_to_commit_ratio"]) / 2.2)
        delivery_risk = min(1.0, (feature_row["open_prs"] / 120) + (feature_row["mean_pr_cycle_time_hours"] / 180))
        code_stability = min(1.0, feature_row["code_churn_rate"] * 0.65 + feature_row["commit_volatility"] * 0.35)
        quality_guardrails = min(1.0, (1 - feature_row["test_coverage"] / 100) * 0.65 + feature_row["ci_failures_rate"] * 0.35)
        team_dynamics = min(1.0, feature_row["developer_load_index"] / 100 + feature_row["bus_factor_inverse"])
        system_fragility_signature = min(
            1.0,
            (feature_row["release_friction_index"] / 5.5) * 0.6 + (feature_row["remediation_latency"] / 120.0) * 0.4,
        )
        coordination_debt_signature = min(
            1.0,
            (feature_row["socio_technical_strain"] / 80.0) * 0.7 + (feature_row["collaboration_imbalance"] / 1.4) * 0.3,
        )
        nlp_signal = min(1.0, nlp_signal_score / 100)

        values = {
            "issue_pressure": issue_pressure,
            "delivery_risk": delivery_risk,
            "code_stability": code_stability,
            "quality_guardrails": quality_guardrails,
            "team_dynamics": team_dynamics,
            "system_fragility_signature": system_fragility_signature,
            "coordination_debt_signature": coordination_debt_signature,
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
        if self.primary_pipeline is None or self.stress_pipeline is None:
            self.train_model()

        features = self._to_feature_vector(feature_payload)
        model = self.primary_pipeline.named_steps["model"]

        base_array = features.values
        base_preds = []
        for est in model.estimators_:
            base_preds.append(float(est.predict(base_array)[0]))

        stress_columns = [
            "issue_momentum",
            "signal_entropy",
            "release_friction_index",
            "socio_technical_strain",
            "remediation_latency",
            "collaboration_imbalance",
            "urgent_signal_ratio",
            "negative_sentiment_ratio",
            "issue_to_commit_ratio",
            "developer_load_index",
            "ci_failures_rate",
            "mean_pr_cycle_time_hours",
        ]

        primary_risk = float(self.primary_pipeline.predict(features)[0])
        stress_risk = float(self.stress_pipeline.predict(features[stress_columns])[0])
        gate = float(
            np.clip(
                0.25
                + (0.35 * features.iloc[0]["signal_entropy"])
                + (0.22 * np.tanh(features.iloc[0]["release_friction_index"] / 2.5))
                + (0.18 * np.tanh(features.iloc[0]["socio_technical_strain"] / 22.0)),
                0.2,
                0.85,
            )
        )

        ml_risk = float((1 - gate) * primary_risk + gate * stress_risk)
        ml_risk = float(np.clip(ml_risk, 0.0, 100.0))

        # Ensemble spread + dual-head disagreement + model RMSE as uncertainty proxy.
        spread = float(np.std(base_preds))
        disagreement = abs(primary_risk - stress_risk)
        rmse = float(self.status.metrics.get("rmse", 6.0))
        uncertainty = float(np.clip((spread * 0.45 + disagreement * 0.25 + rmse * 0.3) / 100, 0.01, 0.6))
        confidence = float(np.clip(1.0 - uncertainty, 0.35, 0.99))

        signal_entropy = float(features.iloc[0]["signal_entropy"])
        nlp_weight = float(np.clip((1 - blend_alpha) + 0.18 * signal_entropy, 0.08, 0.42))
        blended = float(np.clip(((1 - nlp_weight) * ml_risk) + (nlp_weight * nlp_signal_score), 0.0, 100.0))
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
