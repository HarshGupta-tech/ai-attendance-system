import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Video, CheckCircle, Play, XSquare } from 'lucide-react';
import api from '../../utils/api';
import { Button, Card, Badge, LoadingSpinner } from '../../components/common';
import toast from 'react-hot-toast';

export default function SessionDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [session, setSession] = useState(null);
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchDetails = async () => {
    try {
      setLoading(true);
      const res = await api.get(`/attendance/session/${id}`);
      setSession(res.data.session || res.data);
      setRecords(res.data.records || []);
    } catch (err) {
      toast.error('Failed to load session details');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetails();
  }, [id]);

  const updateStatus = async (status) => {
    try {
      if (status === 'active') {
        await api.post(`/attendance/session/${id}/activate`);
      } else if (status === 'completed') {
        await api.post(`/attendance/session/${id}/complete`);
      } else {
        await api.put(`/attendance/session/${id}`, { status });
      }
      toast.success(`Session marked as ${status}`);
      fetchDetails();
    } catch (err) {
      toast.error('Failed to update status');
    }
  };

  if (loading) return <LoadingSpinner />;
  if (!session) return <div>Session not found</div>;

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{session.subjectName}</h1>
          <p className="text-gray-500">{new Date(session.date).toLocaleDateString()} | {session.startTime} - {session.endTime}</p>
        </div>
        <div className="flex gap-2">
          {session.status === 'active' && session.session_code && (
            <div className="bg-teal-100 text-teal-800 px-4 py-2 rounded-lg flex flex-col items-center justify-center mr-4 border border-teal-200">
              <span className="text-xs font-semibold uppercase tracking-wider">Session Code</span>
              <span className="text-xl font-mono font-bold tracking-[0.2em]">{session.session_code}</span>
            </div>
          )}
          {session.status === 'scheduled' && (
            <Button onClick={() => updateStatus('active')} className="bg-green-600 text-white flex items-center gap-2">
              <Play size={16} /> Activate
            </Button>
          )}
          {session.status === 'active' && (
            <>
              <Button onClick={() => navigate('/attendance/live')} className="bg-indigo-600 text-white flex items-center gap-2">
                <Video size={16} /> Go to Live Camera
              </Button>
              <Button onClick={() => updateStatus('completed')} variant="outline" className="flex items-center gap-2">
                <CheckCircle size={16} /> Mark Completed
              </Button>
            </>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="text-center p-4">
          <p className="text-sm text-gray-500">Status</p>
          <Badge className="mt-2" color={session.status === 'active' ? 'green' : session.status === 'completed' ? 'gray' : 'blue'}>
            {session.status.toUpperCase()}
          </Badge>
        </Card>
        <Card className="text-center p-4 bg-green-50 border-green-100">
          <p className="text-sm text-green-600">Present</p>
          <p className="text-2xl font-bold text-green-700">{session.presentCount || 0}</p>
        </Card>
        <Card className="text-center p-4 bg-yellow-50 border-yellow-100">
          <p className="text-sm text-yellow-600">Late</p>
          <p className="text-2xl font-bold text-yellow-700">{session.lateCount || 0}</p>
        </Card>
        <Card className="text-center p-4 bg-red-50 border-red-100">
          <p className="text-sm text-red-600">Absent</p>
          <p className="text-2xl font-bold text-red-700">{session.absentCount || 0}</p>
        </Card>
      </div>

      <Card>
        <h2 className="text-xl font-semibold mb-4">Attendance Records</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b bg-gray-50 text-gray-600 text-sm">
                <th className="p-4">Student ID</th>
                <th className="p-4">Name</th>
                <th className="p-4">Roll No.</th>
                <th className="p-4">Check-in Time</th>
                <th className="p-4">Status</th>
                <th className="p-4">Confidence</th>
              </tr>
            </thead>
            <tbody>
              {records.length > 0 ? records.map((record, idx) => (
                <tr key={idx} className="border-b">
                  <td className="p-4">{record.studentId}</td>
                  <td className="p-4 font-medium">{record.studentName}</td>
                  <td className="p-4">{record.rollNumber}</td>
                  <td className="p-4">{record.checkInTime || '-'}</td>
                  <td className="p-4">
                    <Badge color={record.status === 'present' ? 'green' : record.status === 'late' ? 'yellow' : 'red'}>
                      {record.status}
                    </Badge>
                  </td>
                  <td className="p-4">
                    {record.confidence ? `${(record.confidence * 100).toFixed(1)}%` : '-'}
                  </td>
                </tr>
              )) : (
                <tr><td colSpan="6" className="p-4 text-center text-gray-500">No records found</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
