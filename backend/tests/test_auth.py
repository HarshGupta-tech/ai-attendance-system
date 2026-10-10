def test_login_success(client, admin_user):
    response = client.post("/api/auth/login", json={"username": "testadmin", "password": "Admin@123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == "testadmin"
    assert data["user"]["role"] == "super_admin"

def test_login_wrong_password(client, admin_user):
    response = client.post("/api/auth/login", json={"username": "testadmin", "password": "wrong"})
    assert response.status_code == 401

def test_login_nonexistent_user(client):
    response = client.post("/api/auth/login", json={"username": "nobody", "password": "test"})
    assert response.status_code == 401

def test_get_current_user(client, auth_headers):
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["username"] == "testadmin"

def test_protected_route_no_token(client):
    response = client.get("/api/auth/me")
    assert response.status_code in [401, 403]

def test_change_password(client, auth_headers):
    response = client.post("/api/auth/change-password", headers=auth_headers, json={
        "current_password": "Admin@123",
        "new_password": "NewAdmin@456"
    })
    assert response.status_code == 200
    
    # Login with new password
    response = client.post("/api/auth/login", json={"username": "testadmin", "password": "NewAdmin@456"})
    assert response.status_code == 200

def test_login_disabled_account(client, db_session, admin_user):
    admin_user.is_active = False
    db_session.commit()
    response = client.post("/api/auth/login", json={"username": "testadmin", "password": "Admin@123"})
    assert response.status_code in [401, 403]
