"""The risk tier, following the table in architecture §8."""

from datetime import date

from studio.contracts.app import AppManifest, ConnectorUse
from studio.contracts.common import AccessMode, Audience, DataClassification
from studio.policy.tier import decide_tier

CLASSIFICATIONS: dict[str, DataClassification] = {
    "stores-readonly": "internal",
    "products-readonly": "internal",
    "clients-readonly": "client",
    "legacy-feed": "unknown",
}


def app(audience: Audience = "personal", **connectors: AccessMode) -> AppManifest:
    """An app using the given connectors, written with underscores: stores_readonly="read"."""
    return AppManifest(
        contract_version="1.0.0",
        name="staff-requests",
        owner="00u1a2b3c4D5E6F7g8h9",
        domain="retail",
        project_type="form-workflow",
        connectors=[
            ConnectorUse(id=name.replace("_", "-"), access=access)
            for name, access in connectors.items()
        ],
        audience=audience,
        expires_on=date(2027, 6, 30),
    )


def test_personal_non_sensitive_and_read_only_is_tier_1() -> None:
    decision = decide_tier(app("personal", stores_readonly="read"), CLASSIFICATIONS)

    assert decision.tier == 1
    assert decision.reasons


def test_an_app_with_no_data_is_tier_1() -> None:
    assert decide_tier(app("personal"), CLASSIFICATIONS).tier == 1


def test_sharing_beyond_the_author_is_at_least_tier_2() -> None:
    for audience in ("team", "domain"):
        decision = decide_tier(app(audience, stores_readonly="read"), CLASSIFICATIONS)

        assert decision.tier == 2
        assert any("shared" in reason for reason in decision.reasons)


def test_client_data_is_tier_3() -> None:
    decision = decide_tier(app("personal", clients_readonly="read"), CLASSIFICATIONS)

    assert decision.tier == 3
    assert any("client data" in reason for reason in decision.reasons)


def test_any_write_is_tier_3() -> None:
    decision = decide_tier(app("personal", stores_readonly="write"), CLASSIFICATIONS)

    assert decision.tier == 3
    assert any("writes" in reason for reason in decision.reasons)


def test_unknown_classification_is_tier_3() -> None:
    decision = decide_tier(app("personal", legacy_feed="read"), CLASSIFICATIONS)

    assert decision.tier == 3
    assert any("legacy-feed" in reason for reason in decision.reasons)


def test_a_connector_missing_from_the_classifications_is_tier_3() -> None:
    decision = decide_tier(app("personal", new_feed="read"), CLASSIFICATIONS)

    assert decision.tier == 3
    assert any("new-feed" in reason for reason in decision.reasons)


def test_every_rule_that_applies_gives_its_reason() -> None:
    decision = decide_tier(
        app("team", clients_readonly="read", stores_readonly="write"), CLASSIFICATIONS
    )

    assert decision.tier == 3
    assert len(decision.reasons) == 3
