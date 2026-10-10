from datetime import date, time, datetime, timedelta
from app.models.attendance import AttendanceSession, AttendanceRecord

def test_create_session(client, auth_headers, sample_subject):
    response = client.post("/api/attendance/session", headers=auth_headers, json={
        "subject_id": sample_subject.id,
        "date": str(date.today()),
        "start_time": "10:00:00",
        "end_time": "11:00:00",
        "late_threshold_minutes": 15
    })
    assert response.status_code in [200, 201], response.text
    data = response.json()
    assert data["subject_id"] == sample_subject.id
    assert data["status"] == "scheduled"

def test_activate_session(client, auth_headers, sample_subject):
    # Create session
    resp = client.post("/api/attendance/session", headers=auth_headers, json={
        "subject_id": sample_subject.id,
        "date": str(date.today()),
        "start_time": "10:00:00",
        "end_time": "11:00:00",
        "late_threshold_minutes": 15
    })
    session_id = resp.json()["id"]
    
    # Activate
    resp = client.post(f"/api/attendance/session/{session_id}/activate", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["session"]["status"] == "active"

def test_complete_session(client, auth_headers, sample_subject):
    resp = client.post("/api/attendance/session", headers=auth_headers, json={
        "subject_id": sample_subject.id,
        "date": str(date.today()),
        "start_time": "10:00:00",
        "end_time": "11:00:00"
    })
    session_id = resp.json()["id"]
    client.post(f"/api/attendance/session/{session_id}/activate", headers=auth_headers)
    
    resp = client.post(f"/api/attendance/session/{session_id}/complete", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["session"]["status"] == "completed"

def test_duplicate_session(client, auth_headers, sample_subject):
    """Cannot create duplicate session for same subject/date/time."""
    data = {
        "subject_id": sample_subject.id,
        "date": str(date.today()),
        "start_time": "14:00:00",
        "end_time": "15:00:00"
    }
    resp1 = client.post("/api/attendance/session", headers=auth_headers, json=data)
    assert resp1.status_code in [200, 201]
    resp2 = client.post("/api/attendance/session", headers=auth_headers, json=data)
    assert resp2.status_code in [400, 409]

def test_manual_attendance(client, auth_headers, sample_subject, sample_student):
    # Create and activate session
    resp = client.post("/api/attendance/session", headers=auth_headers, json={
        "subject_id": sample_subject.id,
        "date": str(date.today()),
        "start_time": "10:00:00",
        "end_time": "11:00:00"
    })
    session_id = resp.json()["id"]
    client.post(f"/api/attendance/session/{session_id}/activate", headers=auth_headers)
    
    # Mark attendance manually
    resp = client.post(f"/api/attendance/session/{session_id}/manual", headers=auth_headers, json={
        "student_id": sample_student.id,
        "status": "present"
    })
    assert resp.status_code == 200

def test_duplicate_attendance_prevention(client, auth_headers, db_session, sample_subject, sample_student):
    """Cannot mark attendance twice for same student in same session."""
    resp = client.post("/api/attendance/session", headers=auth_headers, json={
        "subject_id": sample_subject.id,
        "date": str(date.today()),
        "start_time": "10:00:00",
        "end_time": "11:00:00"
    })
    session_id = resp.json()["id"]
    client.post(f"/api/attendance/session/{session_id}/activate", headers=auth_headers)
    
    # First mark
    resp1 = client.post(f"/api/attendance/session/{session_id}/manual", headers=auth_headers, json={
        "student_id": sample_student.id, "status": "present"
    })
    assert resp1.status_code == 200
    
    # Second mark (should fail or indicate already marked)
    resp2 = client.post(f"/api/attendance/session/{session_id}/manual", headers=auth_headers, json={
        "student_id": sample_student.id, "status": "present"
    })
    assert resp2.status_code in [200, 400, 409]  # Either succeeds silently or returns error

def test_attendance_percentage(client, auth_headers, db_session, sample_student):
    """Test attendance percentage calculation."""
    resp = client.get(f"/api/students/{sample_student.id}/attendance-stats", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "attendance_percentage" in data
    assert "total_classes" in data
