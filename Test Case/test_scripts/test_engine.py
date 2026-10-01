# tests for rule engine + decision logic
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pytest

from backend.rules.contradiction_checker import check_contradictions
from backend.rules.duplicate_detector import check_duplicates
from backend.rules.rule_engine import evaluate_rules, load_policy
from ml_service.decision_engine import (
    classify_match_status,
    decide_final_outcome,
    evaluate_claim,
    generate_summary_card,
)

BASE_FEATURES = {
    "claim_id": "CLM-TEST",
    "product_category": "Mobile",
    "product_age_months": 5,
    "warranty_duration_months": 12,
    "remaining_warranty_months": 7,
    "purchase_price": 699.0,
    "fault_type": "display_defect",
    "repair_history_count": 1,
    "unauthorized_repair_flag": 0,
    "serial_number_match": 1,
    "receipt_attached": 1,
    "warranty_card_attached": 1,
    "damage_photo_attached": 1,
    "serial_photo_attached": 1,
    "contradiction_flag": 0,
    "duplicate_flag": 0,
}

CLEAN_RULES = {
    "passed": True,
    "failed_rules": [],
    "findings": {"expired": False, "repair_history_exceeded": False},
}
CLEAN_CONTRA = {"has_contradiction": False, "contradictions": [], "details": {}}
CLEAN_DUPES = {"is_duplicate": False, "duplicate_type": [], "matches": {}}


def _feats(**overrides) -> dict:
    f = dict(BASE_FEATURES)
    f.update(overrides)
    return f


def _run_pipeline(features: dict, tmp_path: Path, **kwargs) -> dict:
    card = tmp_path / f"{features['claim_id']}.png"
    return evaluate_claim(
        features,
        card_out_path=card,
        rule_result=kwargs.get("rule_result", CLEAN_RULES),
        contradiction_result=kwargs.get("contradiction_result", CLEAN_CONTRA),
        duplicate_result=kwargs.get("duplicate_result", CLEAN_DUPES),
    )


def test_valid_claim(tmp_path):
    """In-warranty claim, all docs, clean rules -> Likely Valid (or strong Valid signals)."""
    features = _feats()
    rules = evaluate_rules(
        {
            "damage_type": "display_defect",
            "remaining_warranty_months": 7,
            "unauthorized_repair": 0,
            "repair_history_count": 1,
        },
        {"category": "Mobile", "purchase_date": date.today() - timedelta(days=150)},
        {"expiry_date": date.today() + timedelta(days=200)},
        ["receipt", "warranty_card", "damage_photo", "serial_photo"],
    )
    assert rules["passed"], rules

    result = _run_pipeline(features, tmp_path, rule_result=rules)
    assert result["python_prediction"] in ("Valid", "Manual_Review", "Invalid")
    assert result["gtm_prediction"] in ("Valid", "Manual_Review", "Invalid")
    assert result["final_decision"] in (
        "Likely Valid",
        "Likely Invalid",
        "Manual Review Required",
    )
    # Clean valid features should not hard-fail rules
    assert not any(r.startswith("warranty_expired") for r in result["rule_findings"]["failed_rules"])
    # Primary expectation: both models lean Valid on a clean claim
    assert result["python_prediction"] == "Valid"
    assert result["confidence_difference"] >= 0


def test_invalid_claim(tmp_path):
    """Excluded damage + poor features -> Likely Invalid via hard rule."""
    features = _feats(
        damage_type="liquid_damage",
        fault_type="liquid_damage",
        remaining_warranty_months=-3,
        serial_number_match=0,
        receipt_attached=0,
        contradiction_flag=1,
        unauthorized_repair_flag=1,
    )
    rules = evaluate_rules(
        {
            "damage_type": "liquid_damage",
            "remaining_warranty_months": -3,
            "unauthorized_repair": 1,
            "repair_history_count": 4,
        },
        {"category": "Mobile"},
        {"expiry_date": date.today() - timedelta(days=90)},
        ["damage_photo"],
    )
    assert not rules["passed"]
    assert any(x.startswith("warranty_expired") for x in rules["failed_rules"])
    assert any(x.startswith("excluded_damage") for x in rules["failed_rules"])

    result = _run_pipeline(features, tmp_path, rule_result=rules)
    assert result["final_decision"] == "Likely Invalid"


def test_manual_review_claim(tmp_path):
    """Model disagreement forces Manual Review Required."""
    result = decide_final_outcome(
        "Valid",
        0.88,
        "Invalid",
        0.90,
        "Model Disagreement",
        rule_result=CLEAN_RULES,
        contradiction_result=CLEAN_CONTRA,
        duplicate_result=CLEAN_DUPES,
    )
    assert result["final_decision"] == "Manual Review Required"
    assert any("Disagreement" in e for e in result["explanations"])


def test_expired_warranty(tmp_path):
    features = _feats(remaining_warranty_months=-1, product_age_months=18, warranty_duration_months=12)
    rules = evaluate_rules(
        {
            "damage_type": "battery_failure",
            "remaining_warranty_months": -1,
            "unauthorized_repair": 0,
            "repair_history_count": 0,
        },
        {"category": "Mobile", "purchase_date": date.today() - timedelta(days=550)},
        {"expiry_date": date.today() - timedelta(days=60)},
        ["receipt", "warranty_card", "damage_photo", "serial_photo"],
    )
    assert "warranty_expired" in rules["failed_rules"]

    result = _run_pipeline(features, tmp_path, rule_result=rules)
    assert result["final_decision"] == "Likely Invalid"
    assert "warranty_expired" in result["rule_findings"]["failed_rules"]


def test_missing_mandatory_document(tmp_path):
    rules = evaluate_rules(
        {
            "damage_type": "display_defect",
            "remaining_warranty_months": 6,
            "unauthorized_repair": 0,
            "repair_history_count": 1,
        },
        {"category": "Mobile"},
        {"expiry_date": date.today() + timedelta(days=180)},
        ["receipt"],  # missing warranty_card, damage_photo, serial_photo
    )
    assert not rules["passed"]
    missing = [r for r in rules["failed_rules"] if r.startswith("missing_documents")]
    assert missing, rules["failed_rules"]
    assert "warranty_card" in missing[0]
    assert "damage_photo" in missing[0]

    features = _feats(
        receipt_attached=1,
        warranty_card_attached=0,
        damage_photo_attached=0,
        serial_photo_attached=0,
    )
    result = _run_pipeline(features, tmp_path, rule_result=rules)
    assert result["final_decision"] == "Manual Review Required"


def test_duplicate_document_hash_db():
    """Duplicate detector flags repeated SHA-256 against MySQL."""
    from backend.database.connection import SessionLocal
    from backend.database.models import (
        Claim,
        ClaimStatus,
        Document,
        FileType,
        Product,
        User,
        UserRole,
    )
    from backend.middleware.auth import hash_password
    from backend.ocr.document_parser import compute_sha256

    db = SessionLocal()
    try:
        # Ensure a user exists
        user = db.query(User).filter(User.email == "dup-test@assurex.com").first()
        if not user:
            user = User(
                name="Dup Test",
                email="dup-test@assurex.com",
                password_hash=hash_password("Test@1234"),
                role=UserRole.customer,
            )
            db.add(user)
            db.flush()

        # Create a product for this test claim
        product = Product(
            user_id=user.id,
            product_name="Dup Test Product",
            category="Mobile",
            brand="TestCo",
            model_number="DT-1",
            serial_number="SN-DUP-TEST-001",
            purchase_date=date.today() - timedelta(days=100),
            purchase_price=199.0,
            retailer="TestStore",
            warranty_duration_months=12,
        )
        db.add(product)
        db.flush()

        claim = Claim(
            claim_code="CLAIM-DUP-TEST",
            user_id=user.id,
            product_id=product.id,
            fault_date=date.today(),
            claim_date=date.today(),
            fault_description="dup test",
            damage_type="display_defect",
            status=ClaimStatus.submitted,
        )
        db.add(claim)
        db.flush()

        # Hash of a real project file
        sample = Path("config/settings.json")
        file_hash = compute_sha256(sample)
        doc = Document(
            claim_id=claim.id,
            file_type=FileType.receipt,
            file_path=str(sample),
            file_hash=file_hash,
            extracted_text="INV-DUP-1",
        )
        db.add(doc)
        db.commit()

        # Same hash on a "new" claim -> duplicate
        result = check_duplicates(db, file_hashes=[file_hash], exclude_claim_id=999999)
        assert result["is_duplicate"] is True
        assert "duplicate_document_hash" in result["duplicate_type"]

        # Excluding the same claim -> not a duplicate of itself
        result2 = check_duplicates(db, file_hashes=[file_hash], exclude_claim_id=claim.id)
        assert result2["is_duplicate"] is False

        # Cleanup
        db.delete(claim)
        db.delete(product)
        db.commit()
    finally:
        db.close()


def test_duplicate_decision_forces_manual_review():
    dupes = {
        "is_duplicate": True,
        "duplicate_type": ["duplicate_document_hash"],
        "matches": {},
    }
    result = decide_final_outcome(
        "Valid",
        0.9,
        "Valid",
        0.9,
        "Strong Match",
        rule_result=CLEAN_RULES,
        contradiction_result=CLEAN_CONTRA,
        duplicate_result=dupes,
    )
    assert result["final_decision"] == "Manual Review Required"
    assert "duplicate_document_hash" in result["duplicates"]


def test_contradictory_dates():
    res = check_contradictions(
        {
            "claim_date": date(2025, 1, 1),
            "fault_date": date(2025, 1, 5),
        },
        {"purchase_date": date(2025, 6, 1), "serial_number": "SN-OK"},
        {},
    )
    assert res["has_contradiction"]
    assert "claim_date_before_purchase" in res["contradictions"]
    assert "fault_date_before_purchase" in res["contradictions"]


def test_contradiction_forces_manual_review():
    contra = {
        "has_contradiction": True,
        "contradictions": ["claim_date_before_purchase"],
        "details": {},
    }
    result = decide_final_outcome(
        "Valid",
        0.95,
        "Valid",
        0.93,
        "Strong Match",
        rule_result=CLEAN_RULES,
        contradiction_result=contra,
        duplicate_result=CLEAN_DUPES,
    )
    assert result["final_decision"] == "Manual Review Required"


def test_serial_number_mismatch():
    res = check_contradictions(
        {"claim_date": date.today(), "fault_date": date.today()},
        {"purchase_date": date.today() - timedelta(days=100), "serial_number": "SN-REAL-001"},
        {"serial_number": "SN-FAKE-999"},
    )
    assert "serial_number_mismatch" in res["contradictions"]
    assert res["details"]["registered_serial"] == "SN-REAL-001"
    assert res["details"]["extracted_serial"] == "SN-FAKE-999"


def test_serial_mismatch_flag_in_pipeline(tmp_path):
    features = _feats(serial_number_match=0, contradiction_flag=1)
    contra = {
        "has_contradiction": True,
        "contradictions": ["serial_number_mismatch"],
        "details": {},
    }
    result = _run_pipeline(features, tmp_path, contradiction_result=contra)
    assert result["final_decision"] == "Manual Review Required"
    assert "serial_number_mismatch" in result["rule_findings"]["contradictions"]


def test_unauthorized_repair():
    rules = evaluate_rules(
        {
            "damage_type": "motor_failure",
            "remaining_warranty_months": 6,
            "unauthorized_repair": 1,
            "repair_history_count": 2,
        },
        {"category": "Mobile"},
        {"expiry_date": date.today() + timedelta(days=180)},
        ["receipt", "warranty_card", "damage_photo", "serial_photo"],
    )
    assert "unauthorized_repair" in rules["failed_rules"]

    # Without hard expiry/exclusion, unauthorized repair alone -> review path
    # (not auto-valid because rules failed)
    result = decide_final_outcome(
        "Valid",
        0.9,
        "Valid",
        0.88,
        "Strong Match",
        rule_result=rules,
        contradiction_result=CLEAN_CONTRA,
        duplicate_result=CLEAN_DUPES,
    )
    assert result["final_decision"] != "Likely Valid"
    assert "unauthorized_repair" in result["failed_rules"]


def test_boundary_remaining_warranty_zero():
    """remaining_warranty_months == 0 is expired (<= 0)."""
    rules = evaluate_rules(
        {
            "damage_type": "display_defect",
            "remaining_warranty_months": 0,
            "unauthorized_repair": 0,
            "repair_history_count": 0,
        },
        {"category": "Mobile"},
        {"expiry_date": date.today()},  # expires today
        ["receipt", "warranty_card", "damage_photo", "serial_photo"],
    )
    assert rules["findings"]["expired"] is True
    assert "warranty_expired" in rules["failed_rules"]


def test_boundary_remaining_warranty_one_month_ok():
    rules = evaluate_rules(
        {
            "damage_type": "display_defect",
            "remaining_warranty_months": 1,
            "unauthorized_repair": 0,
            "repair_history_count": 0,
        },
        {"category": "Mobile"},
        {"expiry_date": date.today() + timedelta(days=30)},
        ["receipt", "warranty_card", "damage_photo", "serial_photo"],
    )
    assert rules["findings"]["expired"] is False
    assert "warranty_expired" not in rules["failed_rules"]


def test_boundary_claim_on_purchase_date_ok():
    purchase = date(2026, 3, 1)
    res = check_contradictions(
        {"claim_date": purchase, "fault_date": purchase},
        {"purchase_date": purchase, "serial_number": "SN-1"},
        {"serial_number": "SN-1"},
    )
    assert res["has_contradiction"] is False


def test_dual_model_disagreement_matrix():
    # Classes differ -> Model Disagreement (checked before thresholds)
    m = classify_match_status("Valid", 0.95, "Invalid", 0.95)
    assert m["model_match_status"] == "Model Disagreement"

    # Both same class, very close -> Strong Match
    m = classify_match_status("Valid", 0.95, "Valid", 0.93)
    assert m["model_match_status"] == "Strong Match"
    assert abs(m["confidence_difference"] - 0.02) < 1e-6

    # Same class, moderate gap <= 0.20 -> Acceptable Match
    m = classify_match_status("Valid", 0.90, "Valid", 0.75)
    assert m["model_match_status"] == "Acceptable Match"

    # Same class, gap > 0.20 -> Weak Match
    m = classify_match_status("Valid", 0.95, "Valid", 0.60)
    assert m["model_match_status"] == "Weak Match"

    # Low top confidence < 0.60 -> Uncertain Result
    m = classify_match_status("Manual_Review", 0.55, "Manual_Review", 0.50)
    assert m["model_match_status"] == "Uncertain Result"


def test_thresholds_are_configurable():
    """Thresholds come from config/settings.json."""
    from config.settings import get_thresholds

    th = get_thresholds()
    assert th["strong_match_max_diff"] == 0.10
    assert th["acceptable_match_max_diff"] == 0.20
    assert th["uncertain_min_top_confidence"] == 0.60

    custom = {
        "strong_match_max_diff": 0.05,
        "acceptable_match_max_diff": 0.10,
        "uncertain_min_top_confidence": 0.70,
    }
    m = classify_match_status("Valid", 0.80, "Valid", 0.76, thresholds=custom)
    # diff=0.04 <= 0.05 custom strong
    assert m["model_match_status"] == "Strong Match"
    assert m["thresholds_applied"]["strong_match_max_diff"] == 0.05


def test_disagreement_reaches_final_decision(tmp_path):
    """Full pipeline with forced disagreement path (unit level)."""
    result = decide_final_outcome(
        "Manual_Review",
        0.55,
        "Invalid",
        0.50,
        "Uncertain Result",
        rule_result=CLEAN_RULES,
        contradiction_result=CLEAN_CONTRA,
        duplicate_result=CLEAN_DUPES,
    )
    assert result["final_decision"] == "Manual Review Required"


@pytest.mark.parametrize(
    "category",
    ["Mobile", "Electronics", "Home Appliances"],
)
def test_policies_load(category):
    policy = load_policy(category)
    assert "mandatory_documents" in policy
    assert "excluded_damage_types" in policy
    assert "warranty_duration_months_default" in policy


def test_summary_card_renders_facts_only(tmp_path):
    out = tmp_path / "card.png"
    generate_summary_card(_feats(), out)
    assert out.exists()
    assert out.stat().st_size > 1000
