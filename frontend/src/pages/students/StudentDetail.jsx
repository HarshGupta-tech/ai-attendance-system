import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Edit, Camera, Trash2, User, BookOpen, Calendar, MapPin, Hash, CheckCircle, AlertTriangle } from 'lucide-react';
import api from '../../utils/api';
import { Button, Card, Badge, LoadingSpinner, ConfirmDialog } from '../../components/common';
import toast from 'react-hot-toast';

export default function StudentDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [student, setStudent] = useState(null);
  const [stats, setStats] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showDelete, setShowDelete] = useState(false);

  useEffect(() => {
    const fetchDetails = async () => {
      try {
        setLoading(true);
        const [studentRes, statsRes] = await Promise.all([
          api.get(`/students/${id}`),
          api.get(`/students/${id}/attendance-stats`).catch(() => ({ data: { total: 0, present: 0, late: 0, absent: 0, percentage: 0, history: [] } }))
        ]);
        setStudent(studentRes.data);
        setStats(statsRes.data);
        setHistory(statsRes.data.history || []);
      } catch (err) {
        toast.error('Failed to load student details');
      } finally {
        setLoading(false);
      }
    };
    fetchDetails();
  }, [id]);

  const handleDelete = async () => {
    try {
      await api.del(`/students/${id}`);
      toast.success('Student deleted');
      navigate('/students');
    } catch (err) {
      toast.error('Failed to delete student');
    }
  };

  if (loading) return <LoadingSpinner />;
  if (!student) return <div>Student not found</div>;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{student.fullName}</h1>
          <p className="text-gray-500">ID: {student.studentId} | Roll: {student.rollNumber}</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => navigate(`/students/${id}/edit`)} className="flex items-center gap-2">
            <Edit size={16} /> Edit
          </Button>
          <Button variant="primary" onClick={() => navigate(`/students/${id}/register-face`)} className="flex items-center gap-2 bg-indigo-600 text-white">
            <Camera size={16} /> Register Face
          </Button>
          <Button variant="danger" onClick={() => setShowDelete(true)} className="flex items-center gap-2 bg-red-600 text-white">
            <Trash2 size={16} /> Delete
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Student Info */}
        <Card className="lg:col-span-2">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Student Information</h2>
            <Badge color={student.status === 'active' ? 'green' : 'gray'}>{student.status}</Badge>
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
              <User className="text-gray-400" />
              <div>
                <p className="text-sm text-gray-500">Full Name</p>
                <p className="font-medium">{student.fullName}</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
              <Hash className="text-gray-400" />
              <div>
                <p className="text-sm text-gray-500">Student ID / Roll No</p>
                <p className="font-medium">{student.studentId} / {student.rollNumber}</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
              <BookOpen className="text-gray-400" />
              <div>
                <p className="text-sm text-gray-500">Course & Dept</p>
                <p className="font-medium">{student.course} - {student.department}</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
              <MapPin className="text-gray-400" />
              <div>
                <p className="text-sm text-gray-500">Semester & Section</p>
                <p className="font-medium">Sem {student.semester} - Sec {student.section}</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
              <Calendar className="text-gray-400" />
              <div>
                <p className="text-sm text-gray-500">Admission Date</p>
                <p className="font-medium">{student.dateOfAdmission || 'N/A'}</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
              {student.faceRegistered ? <CheckCircle className="text-green-500" /> : <AlertTriangle className="text-red-500" />}
              <div>
                <p className="text-sm text-gray-500">Face Registration</p>
                <p className={`font-medium ${student.faceRegistered ? 'text-green-600' : 'text-red-600'}`}>
                  {student.faceRegistered ? 'Registered' : 'Not Registered'}
                </p>
              </div>
            </div>
          </div>
        </Card>

        {/* Right Column - Attendance Summary */}
        <Card>
          <h2 className="text-xl font-semibold mb-4">Attendance Summary</h2>
          {stats ? (
            <div className="space-y-6">
              <div className="text-center">
                <div className="text-4xl font-bold text-indigo-600 mb-2">{Math.round(stats.attendance_percentage || 0)}%</div>
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                  <div className={`h-2.5 rounded-full ${(stats.attendance_percentage || 0) >= 75 ? 'bg-green-600' : (stats.attendance_percentage || 0) >= 60 ? 'bg-yellow-400' : 'bg-red-600'}`} style={{ width: `${stats.attendance_percentage || 0}%` }}></div>
                </div>
                <p className="text-sm text-gray-500 mt-2">Overall Attendance</p>
              </div>
              
              <div className="grid grid-cols-2 gap-4 text-center">
                <div className="p-3 bg-blue-50 rounded-lg">
                  <p className="text-xl font-semibold text-blue-700">{stats.total_classes || 0}</p>
                  <p className="text-xs text-blue-600">Total Classes</p>
                </div>
                <div className="p-3 bg-green-50 rounded-lg">
                  <p className="text-xl font-semibold text-green-700">{stats.present}</p>
                  <p className="text-xs text-green-600">Present</p>
                </div>
                <div className="p-3 bg-yellow-50 rounded-lg">
                  <p className="text-xl font-semibold text-yellow-700">{stats.late}</p>
                  <p className="text-xs text-yellow-600">Late</p>
                </div>
                <div className="p-3 bg-red-50 rounded-lg">
                  <p className="text-xl font-semibold text-red-700">{stats.absent}</p>
                  <p className="text-xs text-red-600">Absent</p>
                </div>
              </div>
            </div>
          ) : (
             <p className="text-gray-500">No attendance data available.</p>
          )}
        </Card>
      </div>

      {/* History Table */}
      <Card>
        <h2 className="text-xl font-semibold mb-4">Recent Attendance</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b bg-gray-50 text-gray-600 text-sm">
                <th className="p-4">Date</th>
                <th className="p-4">Subject</th>
                <th className="p-4">Time</th>
                <th className="p-4">Status</th>
              </tr>
            </thead>
            <tbody>
              {history.length > 0 ? history.map((record, idx) => (
                <tr key={idx} className="border-b">
                  <td className="p-4">{new Date(record.date).toLocaleDateString()}</td>
                  <td className="p-4">{record.subjectName}</td>
                  <td className="p-4">{record.checkInTime || '-'}</td>
                  <td className="p-4">
                    <Badge color={record.status === 'present' ? 'green' : record.status === 'late' ? 'yellow' : 'red'}>
                      {record.status}
                    </Badge>
                  </td>
                </tr>
              )) : (
                <tr><td colSpan="4" className="p-4 text-center text-gray-500">No recent records</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {showDelete && (
        <ConfirmDialog
          title="Delete Student"
          message="Are you sure you want to delete this student? This action cannot be undone and will remove all associated attendance records and facial data."
          onConfirm={handleDelete}
          onCancel={() => setShowDelete(false)}
        />
      )}
    </div>
  );
}
