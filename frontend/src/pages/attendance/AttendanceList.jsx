import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Video, Eye, Play, CheckCircle } from 'lucide-react';
import api from '../../utils/api';
import { Button, Card, Badge, LoadingSpinner } from '../../components/common';
import toast from 'react-hot-toast';

export default function AttendanceList() {
  const navigate = useNavigate();
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSessions = async () => {
      try {
        const res = await api.get('/attendance/sessions');
        setSessions(res.data.items || res.data || []);
      } catch (err) {
        toast.error('Failed to load attendance sessions');
      } finally {
        setLoading(false);
      }
    };
    fetchSessions();
  }, []);

  const getStatusColor = (status) => {
    switch(status) {
      case 'active': return 'green';
      case 'scheduled': return 'blue';
      case 'completed': return 'gray';
      case 'cancelled': return 'red';
      default: return 'gray';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <h1 className="text-2xl font-bold text-gray-900">Attendance Sessions</h1>
        <div className="flex gap-2">
          <Button onClick={() => navigate('/attendance/session/create')} className="flex items-center gap-2" variant="outline">
            <Plus size={16} /> Create Session
          </Button>
          <Button onClick={() => navigate('/attendance/live')} className="flex items-center gap-2 bg-green-600 text-white hover:bg-green-700">
            <Video size={16} /> Live Attendance
          </Button>
        </div>
      </div>

      <Card>
        {loading ? (
          <LoadingSpinner />
        ) : sessions.length === 0 ? (
          <div className="text-center py-10 text-gray-500">No attendance sessions found. Create one to start tracking.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b bg-gray-50 text-gray-600 text-sm">
                  <th className="p-4">Date & Time</th>
                  <th className="p-4">Subject</th>
                  <th className="p-4">Class</th>
                  <th className="p-4">Status</th>
                  <th className="p-4">Stats (P/L/A)</th>
                  <th className="p-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {sessions.map((session) => (
                  <tr key={session.id} className="border-b hover:bg-gray-50 cursor-pointer" onClick={() => navigate(`/attendance/session/${session.id}`)}>
                    <td className="p-4">
                      <div className="font-medium">{new Date(session.date).toLocaleDateString()}</div>
                      <div className="text-xs text-gray-500">{session.startTime} - {session.endTime}</div>
                    </td>
                    <td className="p-4 font-medium">{session.subjectName}</td>
                    <td className="p-4 text-sm">{session.course} S{session.semester}-{session.section}</td>
                    <td className="p-4">
                      <Badge color={getStatusColor(session.status)}>{session.status}</Badge>
                    </td>
                    <td className="p-4 text-sm font-medium">
                      <span className="text-green-600">{session.presentCount || 0}</span> / {' '}
                      <span className="text-yellow-600">{session.lateCount || 0}</span> / {' '}
                      <span className="text-red-600">{session.absentCount || 0}</span>
                    </td>
                    <td className="p-4 text-right space-x-2" onClick={e => e.stopPropagation()}>
                      <Button variant="ghost" size="sm" onClick={() => navigate(`/attendance/session/${session.id}`)}><Eye size={16} /></Button>
                      {session.status === 'scheduled' && (
                        <Button variant="ghost" size="sm" className="text-green-600" title="Activate"><Play size={16} /></Button>
                      )}
                      {session.status === 'active' && (
                        <Button variant="ghost" size="sm" className="text-gray-600" title="Complete"><CheckCircle size={16} /></Button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
