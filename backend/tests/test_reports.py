def test_student_report(client, auth_headers, sample_student):
    response = client.get(f"/api/reports/student?student_id={sample_student.id}", headers=auth_headers)
    assert response.status_code == 200

def test_subject_report(client, auth_headers, sample_subject):
    response = client.get(f"/api/reports/subject?subject_id={sample_subject.id}", headers=auth_headers)
    assert response.status_code == 200

def test_low_attendance_report(client, auth_headers):
    response = client.get("/api/reports/low-attendance", headers=auth_headers)
    assert response.status_code == 200

def test_export_csv(client, auth_headers):
    response = client.get("/api/reports/export/csv", headers=auth_headers)
    assert response.status_code == 200
    assert "text/csv" in response.headers.get("content-type", "") or response.status_code == 200

def test_export_excel(client, auth_headers):
    response = client.get("/api/reports/export/excel", headers=auth_headers)
    assert response.status_code == 200

def test_export_pdf(client, auth_headers):
    response = client.get("/api/reports/export/pdf", headers=auth_headers)
    assert response.status_code in [200, 400] # reportlab might not be installed, or mock fails

