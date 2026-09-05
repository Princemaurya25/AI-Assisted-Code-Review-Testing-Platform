def test_full_code_submission_and_review_flow(client, auth_headers):
    # 1. Submit Code
    sub_payload = {
        "title": "Calculator Service",
        "language": "Python",
        "code": "def divide(a, b):\n    return a / b\n",
        "context_description": "Utility function for mathematical division."
    }
    sub_res = client.post("/api/v1/code/submit", json=sub_payload, headers=auth_headers)
    assert sub_res.status_code == 201
    code_id = sub_res.json()["id"]

    # 2. Trigger Review
    rev_res = client.post(f"/api/v1/reviews/{code_id}", headers=auth_headers)
    assert rev_res.status_code == 201
    review_data = rev_res.json()
    review_id = review_data["id"]
    assert "overall_score" in review_data
    assert review_data["status"] == "COMPLETED"

    # 3. Get Review Details
    details_res = client.get(f"/api/v1/reviews/{review_id}", headers=auth_headers)
    assert details_res.status_code == 200
    details = details_res.json()
    assert details["title"] == "Calculator Service"
    assert "findings" in details
    assert "generated_tests" in details
    assert "complexity_metrics" in details

    # 4. Get Dashboard Analytics
    dash_res = client.get("/api/v1/dashboard/stats", headers=auth_headers)
    assert dash_res.status_code == 200
    stats = dash_res.json()
    assert stats["total_reviews"] >= 1
    assert stats["average_score"] > 0
