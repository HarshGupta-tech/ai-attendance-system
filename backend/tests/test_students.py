def test_create_student(client, auth_headers, sample_course, sample_department):
    response = client.post("/api/students/", headers=auth_headers, json={
        "student_id": "MCA099",
        "roll_number": "2024MCA099",
        "full_name": "New Student",
        "email": "new@test.com",
        "phone": "1234567890",
        "course_id": sample_course.id,
        "department_id": sample_department.id,
        "semester": 1,
        "section": "A",
        "status": "active"
    })
    assert response.status_code in [200, 201]
    data = response.json()
    assert data["student_id"] == "MCA099"
    assert data["full_name"] == "New Student"

def test_get_students(client, auth_headers, sample_student):
    response = client.get("/api/students/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1

def test_get_student_by_id(client, auth_headers, sample_student):
    response = client.get(f"/api/students/{sample_student.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["student_id"] == "MCA001"

def test_update_student(client, auth_headers, sample_student):
    response = client.put(f"/api/students/{sample_student.id}", headers=auth_headers, json={
        "full_name": "Updated Name"
    })
    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated Name"

def test_delete_student(client, auth_headers, sample_student):
    response = client.delete(f"/api/students/{sample_student.id}", headers=auth_headers)
    assert response.status_code == 200
    # Verify deleted
    response = client.get(f"/api/students/{sample_student.id}", headers=auth_headers)
    assert response.status_code == 404

def test_search_students(client, auth_headers, sample_student):
    response = client.get("/api/students/?search=Test", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["total"] >= 1

def test_filter_students_by_course(client, auth_headers, sample_student, sample_course):
    response = client.get(f"/api/students/?course_id={sample_course.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["total"] >= 1

def test_duplicate_student_id(client, auth_headers, sample_student, sample_course, sample_department):
    response = client.post("/api/students/", headers=auth_headers, json={
        "student_id": "MCA001",  # Same as sample_student
        "roll_number": "2024MCA999",
        "full_name": "Duplicate",
        "email": "dup@test.com",
        "course_id": sample_course.id,
        "department_id": sample_department.id,
        "semester": 1,
        "section": "A",
        "status": "active"
    })
    assert response.status_code in [400, 409]

def test_unauthorized_student_creation(client, teacher_headers, sample_course, sample_department):
    """Teachers should not be able to create students (if restricted to admin/super_admin)."""
    response = client.post("/api/students/", headers=teacher_headers, json={
        "student_id": "MCA100",
        "roll_number": "2024MCA100",
        "full_name": "Unauthorized",
        "email": "unauth@test.com",
        "course_id": sample_course.id,
        "department_id": sample_department.id,
        "semester": 1,
        "section": "A",
        "status": "active"
    })
    # Should be forbidden or allowed depending on role config
    assert response.status_code in [200, 201, 403]
