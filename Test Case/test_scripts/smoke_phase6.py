"""API smoke tests. Run: python tests/smoke_phase6.py (server must be up)."""
from __future__ import annotations

import io
import time
from datetime import date, timedelta
from pathlib import Path

import httpx

BASE = "http://127.0.0.1:8000"


def main() -> None:
    c = httpx.Client(base_url=BASE, timeout=120.0)

    # 1. Health
    h = c.get("/api/health").json()
    assert h["api"] == "ok" and h["database"] == "ok" and h["python_model"] and h["gtm_model"], h
    print("[1] health OK", h)

    # 2. Admin login
    r = c.post("/api/auth/login", json={"email": "abdulrafay.dev00@gmail.com", "password": "Password@123"})
    assert r.status_code == 200, r.text
    admin_h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    print("[2] admin login OK")

    # 3. Customer login
    r = c.post("/api/auth/login", json={"email": "umer@gmail.com", "password": "Password@123"})
    assert r.status_code == 200, r.text
    cust_h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    print("[3] customer login OK")

    # 4. Reviewer login
    r = c.post("/api/auth/login", json={"email": "veeraj@gmail.com", "password": "Password@123"})
    assert r.status_code == 200, r.text
    rev_h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    print("[4] reviewer login OK")

    # 5. Products
    r = c.get("/api/products", headers=cust_h)
    assert r.status_code == 200, r.text
    products = r.json()
    print("[5] products OK, count=", len(products))

    # 6. New product
    purchase = date.today() - timedelta(days=100)
    body = {
        "product_name": "Smoke Test Phone",
        "category": "Mobile",
        "brand": "TestCo",
        "model_number": "TC-99",
        "serial_number": f"SN-SMOKE-{int(time.time())}",
        "purchase_date": purchase.isoformat(),
        "purchase_price": 499.0,
        "retailer": "SmokeStore",
        "warranty_duration_months": 12,
    }
    r = c.post("/api/products", json=body, headers=cust_h)
    assert r.status_code == 201, r.text
    pid2 = r.json()["id"]
    print("[6] product created id=", pid2)

    # 7. Create claim
    claim_body = {
        "product_id": pid2,
        "fault_date": (date.today() - timedelta(days=5)).isoformat(),
        "claim_date": date.today().isoformat(),
        "fault_description": "Screen has intermittent flicker",
        "damage_type": "intermittent_fault",
        "fault_type": "screen_flicker",
        "repair_history_count": 1,
        "unauthorized_repair": 0,
    }
    r = c.post("/api/claims", json=claim_body, headers=cust_h)
    assert r.status_code == 201, r.text
    claim = r.json()
    cid = claim["id"]
    print("[7] claim created", claim["claim_code"], "status=", claim["status"])

    # 8. Upload documents
    from PIL import Image

    files = {}
    for name, color in [
        ("receipt", (240, 240, 240)),
        ("warranty_card", (230, 240, 255)),
        ("damage_photo", (255, 220, 220)),
        ("serial_photo", (220, 255, 220)),
    ]:
        buf = io.BytesIO()
        Image.new("RGB", (480, 320), color).save(buf, "PNG")
        files[name] = (f"{name}.png", buf.getvalue(), "image/png")
    r = c.post(f"/api/claims/{cid}/documents", files=files, headers=cust_h)
    assert r.status_code == 201, r.text
    docs = r.json()
    assert len(docs) == 4, docs
    assert all(len(d["file_hash"]) == 64 for d in docs)
    print("[8] 4 documents uploaded, SHA-256 OK")

    # 9. Evaluate dual-model
    t0 = time.time()
    r = c.post(f"/api/claims/{cid}/evaluate", headers=cust_h)
    elapsed = time.time() - t0
    assert r.status_code == 200, r.text
    ev = r.json()
    print(f"[9] evaluate OK in {elapsed:.2f}s ({ev['duration_ms']} ms)")
    print("    python:", ev["python_prediction"], ev["python_confidence"])
    print("    gtm:   ", ev["gtm_prediction"], ev["gtm_confidence"])
    print("    diff:  ", ev["confidence_difference"], ev["model_match_status"])
    print("    FINAL: ", ev["final_decision"])
    assert ev["final_decision"] in (
        "Likely Valid",
        "Likely Invalid",
        "Manual Review Required",
    )
    assert ev["confidence_difference"] is not None
    if elapsed > 5:
        print(f"    warning: evaluation took {elapsed:.2f}s (target <=5s)")

    # 10. Persisted claim
    r = c.get(f"/api/claims/{cid}", headers=cust_h)
    persisted = r.json()
    assert persisted["python_prediction"] and persisted["gtm_prediction"]
    assert persisted["final_decision"] == ev["final_decision"]
    print("[10] claim persisted OK, decision=", persisted["final_decision"])

    # 11. Reviewer override
    r = c.post(
        f"/api/claims/{cid}/review",
        json={"decision": "Approved", "comments": "Smoke test approval"},
        headers=rev_h,
    )
    assert r.status_code == 200, r.text
    print("[11] reviewer override OK ->", r.json()["final_decision"])

    # 12. Audit log
    r = c.get(f"/api/claims/{cid}/audit", headers=rev_h)
    assert r.status_code == 200
    actions = [a["action"] for a in r.json()]
    assert "claim_created" in actions
    assert "dual_model_evaluation" in actions
    assert "reviewer_override" in actions
    print("[12] audit log OK:", actions)

    # 13. Admin analytics
    r = c.get("/api/admin/analytics", headers=admin_h)
    assert r.status_code == 200
    an = r.json()
    assert an["total_claims"] >= 1
    print(
        "[13] analytics OK: total=",
        an["total_claims"],
        "decisions=",
        an["by_decision"],
        "disagreement_rate=",
        an["disagreement_rate"],
    )

    # 14. CSV export
    r = c.get("/api/admin/export/claims.csv", headers=admin_h)
    assert r.status_code == 200 and "text/csv" in r.headers["content-type"]
    assert "claim_code" in r.text
    print("[14] CSV export OK,", len(r.text.splitlines()), "lines")

    # 15. Static upload served
    uploaded = list(Path("uploads").rglob(f"*c{cid}_*"))
    assert uploaded, "no uploaded file found"
    rel = uploaded[0].as_posix().replace("\\", "/")
    r = c.get("/" + rel)
    assert r.status_code == 200 and r.headers["content-type"].startswith("image")
    print("[15] static /uploads OK:", rel)

    print()
    print("all smoke tests passed")


if __name__ == "__main__":
    main()
