def test_create_subject(client, auth_headers, sample_course, sample_department):
    response = client.post("/api/subjects/", headers=auth_headers, json={
        "code": "CS101",
        "name": "Intro to CS",
        "course_id": sample_course.id,
        "department_id": sample_department.id,
        "semester": 1,
        "credits": 3
    })
    assert response.status_code in [200, 201]
    assert response.json()["code"] == "CS101"

def test_get_subjects(client, auth_headers, sample_subject):
    response = client.get("/api/subjects/", headers=auth_headers)
    assert response.status_code == 200

def test_get_subject_by_id(client, auth_headers, sample_subject):
    response = client.get(f"/api/subjects/{sample_subject.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["code"] == "ML101"

def test_update_subject(client, auth_headers, sample_subject):
    response = client.put(f"/api/subjects/{sample_subject.id}", headers=auth_headers, json={
        "name": "Advanced Machine Learning"
    })
    assert response.status_code == 200

def test_delete_subject(client, auth_headers, sample_subject):
    response = client.delete(f"/api/subjects/{sample_subject.id}", headers=auth_headers)
    assert response.status_code == 200
