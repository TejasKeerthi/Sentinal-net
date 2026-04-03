# Sentinel-Net Niche Model Positioning

## Model Identity
- Name: Dual-Head Adaptive Risk Fusion (DHARF)
- Version: 2.0.0
- Domain: Software repository reliability risk prediction

## Core Novel Components
1. Dual-head prediction architecture
- Primary head: stacking ensemble for broad repository behavior modeling.
- Stress head: specialized regressor focused on instability and coordination stress signatures.

2. Adaptive fusion gate
- Final ML score is a dynamic fusion of both heads.
- Gate strength increases under high signal entropy, high release friction, and high socio-technical strain.

3. Reliability signature feature family
- issue_momentum
- signal_entropy
- release_friction_index
- socio_technical_strain
- remediation_latency
- collaboration_imbalance

4. Uncertainty estimation
- Combines base ensemble spread, dual-head disagreement, and holdout RMSE.
- Produces confidence and uncertainty for decision support and risk explainability.

5. Dynamic NLP blend
- NLP influence is not fixed; it increases with signal entropy.
- Enables context-sensitive fusion between quantitative repo telemetry and semantic risk signals.

## Claim-Oriented Differentiators (Technical)
- A dual-head risk model where one head is general reliability and a second head is stress-specialized.
- A runtime gating function driven by engineered repository instability signatures.
- A confidence output derived from both model disagreement and ensemble variance.
- Entropy-conditioned blending of NLP risk signal with ML structural risk score.

## Artifact Evidence in This Codebase
- Training/inference implementation: backend/ml_models.py
- Feature production pipeline: backend/github_analyzer.py
- Runtime status endpoint: GET /api/health

## Notes
- This document is technical support material, not legal advice.
- Patent filing strategy, claim language, and prior-art analysis should be finalized with a patent attorney.
