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
from studio.contracts.common import ConnectorId, RiskTier


class TierDecision(BaseModel):
    model_config = ConfigDict(frozen=True)

    tier: RiskTier
    reasons: list[str]
    """Why the app has this tier, in plain words."""


def _critical_reasons(app: AppManifest, classifications: Mapping[ConnectorId, str]) -> list[str]:
    reasons: list[str] = []
    for connector, access in app.connectors.items():
        # Fail safe: anything but `internal`, including a missing or misspelled label, is sensitive.
        classification = classifications.get(connector)
        if classification == "client":
            reasons.append(f"It reads client data from {connector}.")
        elif classification != "internal":
            reasons.append(
                f"The data in {connector} has no known classification, "
                "so it's treated as sensitive."
            )
        if access == "write":
            reasons.append(f"It writes to {connector}.")
    return reasons


def decide_tier(app: AppManifest, classifications: Mapping[ConnectorId, str]) -> TierDecision:
    """The app's tier, from its `app.yaml` and the data classification of each connector.

    `classifications` comes from the domain pack (step 11), later from Dataplex (step 26). Only
    `internal` counts as non-sensitive: `client`, `unknown`, a missing connector or any other
    label gives tier 3.
    """
    shared = (
        [f"It's shared beyond its author ({app.audience})."] if app.audience != "personal" else []
    )
    critical = _critical_reasons(app, classifications)
    tier: RiskTier = 3 if critical else 2 if shared else 1
    reasons = shared + critical or [
        "Only its author uses it, and it reads non-sensitive data without writing."
    ]
    return TierDecision(tier=tier, reasons=reasons)
