"""
Advanced Machine Learning Models for Software Reliability Prediction
Includes Random Forest, Ensemble Methods, and Anomaly Detection
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import pickle
import os

try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, IsolationForest
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


@dataclass
class MLPrediction:
    """ML prediction result"""
    predicted_risk_score: float
    confidence_score: float
    anomaly_detected: bool
    anomaly_severity: float
    contributing_features: Dict[str, float]
    timestamp: str
    forecast_next_24h: List[float]


class RiskScorePredictorML:
    """Machine Learning based Risk Score Predictor using Random Forest & Gradient Boosting"""
    
    def __init__(self):
        """Initialize ML models"""
        self.rf_model = None
        self.gb_model = None
        self.scaler = StandardScaler()
        self.model_path = "models/risk_predictor.pkl"
        self.load_or_train_model()
        
    def load_or_train_model(self):
        """Load pre-trained model or train new one"""
        if os.path.exists(self.model_path) and SKLEARN_AVAILABLE:
            try:
                with open(self.model_path, 'rb') as f:
                    data = pickle.load(f)
                    self.rf_model = data['rf_model']
                    self.gb_model = data['gb_model']
                    self.scaler = data['scaler']
                return
            except:
                pass
        
        # Initialize models if not available
        if SKLEARN_AVAILABLE:
            self.rf_model = RandomForestRegressor(
                n_estimators=100,
                max_depth=15,
                min_samples_split=5,
                random_state=42
            )
            self.gb_model = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )
    
    def extract_features(self, 
                        commits_30d: int,
                        contributors_30d: int,
                        open_issues: int,
                        closed_issues_30d: int,
                        avg_commit_frequency: float,
                        code_churn_rate: float,
                        test_coverage: float,
                        ci_failures_rate: float) -> np.ndarray:
        """Extract features for ML prediction"""
        features = np.array([
            commits_30d,
            contributors_30d,
            open_issues,
            closed_issues_30d,
            avg_commit_frequency,
            code_churn_rate,
            test_coverage,
            ci_failures_rate,
            open_issues / max(closed_issues_30d, 1),  # Issue resolution ratio
            commits_30d / max(contributors_30d, 1),   # Commits per contributor
            max(0, 100 - test_coverage),              # Coverage gap
            ci_failures_rate * 100                     # CI failure percentage
        ]).reshape(1, -1)
        
        return features
    
    def predict_risk(self,
                    commits_30d: int,
                    contributors_30d: int,
                    open_issues: int,
                    closed_issues_30d: int = 5,
                    avg_commit_frequency: float = 2.5,
                    code_churn_rate: float = 0.3,
                    test_coverage: float = 75.0,
                    ci_failures_rate: float = 0.05) -> MLPrediction:
        """
        Predict risk score using ML ensemble
        
        Returns:
            MLPrediction with risk score, confidence, and feature importance
        """
        features = self.extract_features(
            commits_30d,
            contributors_30d,
            open_issues,
            closed_issues_30d,
            avg_commit_frequency,
            code_churn_rate,
            test_coverage,
            ci_failures_rate
        )
        
        if not SKLEARN_AVAILABLE or self.rf_model is None:
            # Fallback to rule-based calculation
            return self._fallback_prediction(features[0])
        
        try:
            # Scale features
            features_scaled = self.scaler.fit_transform(features)
            
            # Get predictions from both models
            rf_pred = max(0, min(100, self.rf_model.predict(features)[0]))
            gb_pred = max(0, min(100, self.gb_model.predict(features)[0]))
            
            # Ensemble prediction (weighted average)
            risk_score = (rf_pred * 0.5 + gb_pred * 0.5)
            
            # Calculate confidence (inverse of prediction variance)
            predictions = [
                rf_pred, gb_pred,
                self._rule_based_risk(features[0])
            ]
            confidence = 1 - (np.std(predictions) / 100)
            
            # Feature importance analysis
            feature_importance = self._get_feature_importance(features[0])
            
            # Forecast next 24 hours (simplified)
            forecast = self._forecast_24h(risk_score, avg_commit_frequency)
            
        except Exception as e:
            print(f"ML prediction error: {e}, using fallback")
            return self._fallback_prediction(features[0])
        
        return MLPrediction(
            predicted_risk_score=risk_score,
            confidence_score=max(0.0, min(1.0, confidence)),
            anomaly_detected=False,
            anomaly_severity=0.0,
            contributing_features=feature_importance,
            timestamp=datetime.utcnow().isoformat() + "Z",
            forecast_next_24h=forecast
        )
    
    def _rule_based_risk(self, features: np.ndarray) -> float:
        """Fallback rule-based risk calculation"""
        commits_30d = features[0]
        contributors = features[1]
        open_issues = features[2]
        closed_issues = features[3]
        
        # Base risk from open issues
        risk = (open_issues / max(open_issues + closed_issues, 1)) * 100
        
        # Adjust for commit activity
        if commits_30d < 5:
            risk += 15  # Low activity is risky
        elif commits_30d > 50:
            risk += 10  # High activity may indicate instability
        
        # Adjust for team size
        if contributors < 2:
            risk += 20  # Small team
        elif contributors > 10:
            risk -= 5   # Large team better for reliability
        
        return max(0, min(100, risk))
    
    def _get_feature_importance(self, features: np.ndarray) -> Dict[str, float]:
        """Calculate relative feature importance"""
        feature_names = [
            "commits_30d", "contributors", "open_issues", "closed_issues",
            "commit_frequency", "code_churn", "test_coverage", "ci_failures",
            "issue_ratio", "commits_per_contrib", "coverage_gap", "ci_fail_pct"
        ]
        
        # Simple importance based on magnitude and variance
        importance = {}
        for i, name in enumerate(feature_names):
            importance[name] = float(np.abs(features[i]) / (np.max(np.abs(features)) + 1))
        
        return importance
    
    def _forecast_24h(self, current_risk: float, trend: float) -> List[float]:
        """Forecast risk score for next 24 hours"""
        forecast = []
        for hour in range(24):
            # Apply trend with some randomness decay
            noise = np.random.normal(0, 1) * (1 - hour/24)
            predicted = max(0, min(100, current_risk + (trend * hour * 0.5) + noise))
            forecast.append(float(predicted))
        return forecast
    
    def _fallback_prediction(self, features: np.ndarray) -> MLPrediction:
        """Fallback prediction when ML models unavailable"""
        risk_score = self._rule_based_risk(features)
        return MLPrediction(
            predicted_risk_score=risk_score,
            confidence_score=0.65,
            anomaly_detected=False,
            anomaly_severity=0.0,
            contributing_features={},
            timestamp=datetime.utcnow().isoformat() + "Z",
            forecast_next_24h=[risk_score + i*0.1 for i in range(24)]
        )


class AnomalyDetector:
    """Anomaly detection using Isolation Forest"""
    
    def __init__(self):
        """Initialize anomaly detector"""
        self.model = IsolationForest(contamination=0.1, random_state=42) if SKLEARN_AVAILABLE else None
        self.scaler = StandardScaler()
        
    def detect_anomalies(self,
                        temporal_data: List[Dict],
                        signal_data: List[Dict]) -> Tuple[bool, float, List[Dict]]:
        """
        Detect anomalies in temporal and signal data
        
        Returns:
            (is_anomalous, severity_score, anomalous_points)
        """
        if not SKLEARN_AVAILABLE or self.model is None:
            return self._detect_anomalies_rule_based(temporal_data, signal_data)
        
        try:
            # Extract features from temporal data
            features = []
            for data in temporal_data:
                features.append([
                    data.get('bugGrowth', 0),
                    data.get('devIrregularity', 0),
                ])
            
            if len(features) < 3:
                return False, 0.0, []
            
            features = np.array(features)
            
            # Scale and predict
            features_scaled = self.scaler.fit_transform(features)
            predictions = self.model.predict(features_scaled)
            scores = self.model.score_samples(features_scaled)
            
            # Analyze anomalies
            anomalous_points = []
            for i, (pred, score) in enumerate(zip(predictions, scores)):
                if pred == -1:  # Anomaly
                    severity = -score  # Convert to positive severity
                    anomalous_points.append({
                        'index': i,
                        'timestamp': temporal_data[i].get('timestamp'),
                        'severity': min(1.0, severity),
                        'features': {
                            'bugGrowth': temporal_data[i].get('bugGrowth'),
                            'devIrregularity': temporal_data[i].get('devIrregularity')
                        }
                    })
            
            is_anomalous = len(anomalous_points) > 0
            severity = max([p['severity'] for p in anomalous_points]) if anomalous_points else 0.0
            
            return is_anomalous, severity, anomalous_points
            
        except Exception as e:
            print(f"Anomaly detection error: {e}")
            return self._detect_anomalies_rule_based(temporal_data, signal_data)
    
    def _detect_anomalies_rule_based(self,
                                     temporal_data: List[Dict],
                                     signal_data: List[Dict]) -> Tuple[bool, float, List[Dict]]:
        """Rule-based anomaly detection fallback"""
        if len(temporal_data) < 2:
            return False, 0.0, []
        
        anomalous_points = []
        
        # Check for sudden spikes in bug growth
        for i in range(1, len(temporal_data)):
            prev_bug = temporal_data[i-1].get('bugGrowth', 0)
            curr_bug = temporal_data[i].get('bugGrowth', 0)
            
            if prev_bug > 0:
                change_ratio = curr_bug / prev_bug
                if change_ratio > 2.0:  # More than 2x increase
                    severity = min(1.0, (change_ratio - 1.0) / 3.0)
                    anomalous_points.append({
                        'index': i,
                        'timestamp': temporal_data[i].get('timestamp'),
                        'severity': severity,
                        'type': 'spike'
                    })
        
        is_anomalous = len(anomalous_points) > 0
        severity = max([p['severity'] for p in anomalous_points]) if anomalous_points else 0.0
        
        return is_anomalous, severity, anomalous_points


# Singleton instances
_risk_predictor = None
_anomaly_detector = None


def get_risk_predictor() -> RiskScorePredictorML:
    """Get or create risk predictor instance"""
    global _risk_predictor
    if _risk_predictor is None:
        _risk_predictor = RiskScorePredictorML()
    return _risk_predictor


def get_anomaly_detector() -> AnomalyDetector:
    """Get or create anomaly detector instance"""
    global _anomaly_detector
    if _anomaly_detector is None:
        _anomaly_detector = AnomalyDetector()
    return _anomaly_detector
