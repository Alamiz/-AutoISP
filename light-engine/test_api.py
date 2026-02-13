"""Quick smoke test for all API endpoints."""
import urllib.request
import json

BASE = "http://localhost:8000/api"

def post(path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(f"{BASE}{path}", data=data, headers={"Content-Type": "application/json"})
    r = urllib.request.urlopen(req)
    return json.loads(r.read())

def get(path):
    r = urllib.request.urlopen(f"{BASE}{path}")
    return json.loads(r.read())

def patch(path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(f"{BASE}{path}", data=data, headers={"Content-Type": "application/json"}, method="PATCH")
    r = urllib.request.urlopen(req)
    return json.loads(r.read())

# ── 1. Accounts bulk upsert ──
print("=" * 60)
print("1. POST /accounts/bulk-upsert")
acc_result = post("/accounts/bulk-upsert", [
    {"email": "a@gmx.net", "password": "pass1", "provider": "gmx"},
    {"email": "b@gmx.net", "password": "pass2", "provider": "gmx", "status": "active"},
    {"email": "c@webde.de", "password": "pass3", "provider": "webde"},
])
print(f"   Result: {acc_result}")
assert len(acc_result["created_ids"]) == 3, "Expected 3 created accounts"
print("   PASS")

# ── 2. Proxies bulk upsert ──
print("\n2. POST /proxies/bulk-upsert")
proxy_result = post("/proxies/bulk-upsert", [
    {"ip": "192.168.1.1", "port": 8080, "username": "user1", "password": "ppass1"},
    {"ip": "10.0.0.1", "port": 3128},
    {"ip": "172.16.0.1", "port": 1080, "username": "user3"},
])
print(f"   Result: {proxy_result}")
assert len(proxy_result["created_ids"]) == 3, "Expected 3 created proxies"
print("   PASS")

# ── 3. GET /accounts (with search) ──
print("\n3. GET /accounts?search=gmx")
accounts = get("/accounts?search=gmx")
print(f"   Total: {accounts['total']}, Items: {len(accounts['items'])}")
assert accounts["total"] == 2, "Expected 2 GMX accounts"
print("   PASS")

# ── 4. GET /accounts with provider filter ──
print("\n4. GET /accounts?provider=webde")
accounts_webde = get("/accounts?provider=webde")
print(f"   Total: {accounts_webde['total']}")
assert accounts_webde["total"] == 1, "Expected 1 webde account"
print("   PASS")

# ── 5. PATCH /accounts/{id} ──
print("\n5. PATCH /accounts/1")
patched = patch("/accounts/1", {"status": "active", "phone_number": "+123456"})
print(f"   Status: {patched['status']}, Phone: {patched['phone_number']}")
assert patched["status"] == "active"
assert patched["phone_number"] == "+123456"
print("   PASS")

# ── 6. POST /jobs/run ──
print("\n6. POST /jobs/run")
pid1, pid2 = proxy_result["created_ids"][0], proxy_result["created_ids"][1]
job = post("/jobs/run", {
    "name": "GMX batch test",
    "max_concurrent": 3,
    "accounts": [
        {"email": "a@gmx.net", "password": "pass1_updated", "provider": "gmx"},
        {"email": "d@gmx.net", "password": "pass4", "provider": "gmx"},
    ],
    "proxy_ids": [pid1, pid2],
    "automations": [
        {"automation_name": "report_not_spam", "run_order": 1, "settings": {"keyword": "Invoice"}, "enabled": True},
        {"automation_name": "open_links", "run_order": 2, "settings": {"max": 10}, "enabled": True},
    ],
})
print(f"   Job ID: {job['id']}, Status: {job['status']}, Name: {job['name']}")
assert job["status"] == "queued"
print("   PASS")

# ── 7. GET /jobs ──
print("\n7. GET /jobs")
jobs = get("/jobs")
print(f"   Total: {jobs['total']}")
assert jobs["total"] >= 1
print("   PASS")

# ── 8. GET /jobs/{id}/summary ──
print("\n8. GET /jobs/{id}/summary")
summary = get(f"/jobs/{job['id']}/summary")
print(f"   Accounts: {summary['accounts_count']}, Proxies: {summary['proxies_count']}, Automations: {len(summary['automations'])}")
print(f"   Job Accounts: {summary['job_accounts']}")
assert summary["accounts_count"] == 2, "Expected 2 accounts in job"
assert summary["proxies_count"] == 2, "Expected 2 proxies used"
assert len(summary["automations"]) == 2, "Expected 2 automations"
print("   PASS")

# ── 9. Idempotent re-upsert ──
print("\n9. POST /accounts/bulk-upsert (re-upsert same accounts)")
acc_result2 = post("/accounts/bulk-upsert", [
    {"email": "a@gmx.net", "password": "pass1", "provider": "gmx"},
    {"email": "b@gmx.net", "password": "pass2", "provider": "gmx"},
])
print(f"   Result: {acc_result2}")
assert len(acc_result2["created_ids"]) == 0, "Expected 0 new (all existing)"
assert len(acc_result2["existing_ids"]) == 2, "Expected 2 existing"
print("   PASS")

# ── 10. GET /proxies ──
print("\n10. GET /proxies")
proxies = get("/proxies")
print(f"   Total: {proxies['total']}")
assert proxies["total"] == 3
print("   PASS")

print("\n" + "=" * 60)
print("ALL TESTS PASSED!")
