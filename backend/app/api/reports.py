from fastapi import APIRouter, Depends, HTTPException, Query, Response, Request
from sqlalchemy.orm import Session
from typing import Any, Optional

from app.core.dependencies import get_db, get_current_user, require_role
from app.services.report_service import ReportService
from app.schemas import report as report_schemas
from app.models.user import User

router = APIRouter()


@router.get("/attendance")
def get_attendance_report(
    date_range: Optional[str] = None,
    student_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    course_id: Optional[int] = None,
    semester: Optional[int] = None,
    section: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = ReportService(db)
        return service.generate_attendance_report(
            {"date_range": date_range, "student_id": student_id, "subject_id": subject_id,
            "course_id": course_id, "semester": semester, "section": section, "status": status}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/student")
def get_student_report(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = ReportService(db)
        return service.generate_student_report(student_id=student_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/subject")
def get_subject_report(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = ReportService(db)
        return service.generate_subject_report(subject_id=subject_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/low-attendance")
def get_low_attendance_report(
    threshold: float = Query(75.0, ge=0.0, le=100.0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = ReportService(db)
        return service.generate_low_attendance_report(threshold=threshold)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/export/csv")
def export_csv(
    request: Request,
    date_range: Optional[str] = None,
    student_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    course_id: Optional[int] = None,
    semester: Optional[int] = None,
    section: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = ReportService(db)
        data = service.generate_attendance_report(
            {"date_range": date_range, "student_id": student_id, "subject_id": subject_id,
            "course_id": course_id, "semester": semester, "section": section, "status": status}
        )
        columns = list(data[0].keys()) if data else []
        csv_data = service.export_csv(data, columns)
        return Response(content=csv_data, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=report.csv"})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/export/excel")
def export_excel(
    request: Request,
    date_range: Optional[str] = None,
    student_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = ReportService(db)
        data = service.generate_attendance_report(
            {"date_range": date_range, "student_id": student_id, "subject_id": subject_id}
        )
        columns = list(data[0].keys()) if data else []
        excel_data = service.export_excel(data, columns)
        return Response(content=excel_data, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=report.xlsx"})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/export/pdf")
def export_pdf(
    request: Request,
    date_range: Optional[str] = None,
    student_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        service = ReportService(db)
        data = service.generate_attendance_report(
            {"date_range": date_range, "student_id": student_id, "subject_id": subject_id}
        )
        columns = list(data[0].keys()) if data else []
        pdf_data = service.export_pdf(data, columns)
        return Response(content=pdf_data, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=report.pdf"})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))