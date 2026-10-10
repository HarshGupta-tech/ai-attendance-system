def test_dashboard_stats(client, auth_headers):
    response = client.get("/api/dashboard/statistics", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "stats" in data
    stats = data["stats"]
    assert "total_students" in stats
    assert "present_today" in stats
    assert "absent_today" in stats
    assert "late_today" in stats

def test_dashboard_requires_auth(client):
    response = client.get("/api/dashboard/statistics")
    assert response.status_code in [401, 403]
