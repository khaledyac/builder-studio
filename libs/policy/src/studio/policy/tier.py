"""The risk tier of an app, following the table in architecture §8.

| Tier | Data and users |
|---|---|
| 1 · Personal | Author only, no sensitive data, read-only |
| 2 · Team | Internal data, read-only, shared |
| 3 · Critical | Client data or write access |

The tier only goes up: each rule that applies raises it and says why.
"""

from collections.abc import Mapping

from pydantic import BaseModel, ConfigDict

from studio.contracts.app import AppManifest
from studio.contracts.common import DataClassification, RiskTier


class TierDecision(BaseModel):
    model_config = ConfigDict(frozen=True)

    tier: RiskTier
    reasons: list[str]
    """Why the app has this tier, in plain words."""


def _critical_reasons(
    app: AppManifest, classifications: Mapping[str, DataClassification]
) -> list[str]:
    reasons: list[str] = []
    for connector in app.connectors:
        # A connector missing from the classifications is unknown: fail safe.
        classification = classifications.get(connector.id, "unknown")
        if classification == "client":
            reasons.append(f"It reads client data from {connector.id}.")
        elif classification == "unknown":
            reasons.append(
                f"The data in {connector.id} isn't classified, so it's treated as sensitive."
            )
        if connector.access == "write":
            reasons.append(f"It writes to {connector.id}.")
    return reasons


def decide_tier(
    app: AppManifest, classifications: Mapping[str, DataClassification]
) -> TierDecision:
    """The app's tier, from its `app.yaml` and the data classification of each connector."""
    shared = (
        [f"It's shared beyond its author ({app.audience})."] if app.audience != "personal" else []
    )
    critical = _critical_reasons(app, classifications)
    tier: RiskTier = 3 if critical else 2 if shared else 1
    reasons = shared + critical or [
        "Only its author uses it, and it reads non-sensitive data without writing."
    ]
    return TierDecision(tier=tier, reasons=reasons)
