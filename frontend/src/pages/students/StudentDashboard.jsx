import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, BookOpen, Clock, AlertTriangle, CalendarCheck, CheckCircle, XCircle, Camera } from 'lucide-react';
import api from '../../utils/api';
import { Card, Badge, Button } from '../../components/common';
import { useAuth } from '../../contexts/AuthContext';

export default function StudentDashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // First get the student profile
        const profileRes = await api.get('/students/me');
        const studentData = profileRes.data;
        setProfile(studentData);

        // Then get their attendance stats
        if (studentData && studentData.id) {
          try {
            const statsRes = await api.get(`/students/${studentData.id}/attendance-stats`);
            setStats(statsRes.data);
          } catch (err) {
            console.error('Failed to load stats', err);
            // Provide default empty stats if it fails
            setStats({ total: 0, present: 0, absent: 0, late: 0, percentage: 0, history: [] });
          }
        }
      } catch (err) {
        console.error('Failed to load student profile', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64 text-teal-600">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-600"></div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="p-8 text-center text-gray-500">
        <p className="text-xl">Your student profile could not be found.</p>
        <p className="mt-2 text-sm">Please contact your administrator if you believe this is an error.</p>
      </div>
    );
  }

  // Fallback to empty stats if none returned
  const s = stats || { total_classes: 0, present: 0, absent: 0, late: 0, attendance_percentage: 0, history: [] };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      
      {/* Student Welcome Banner */}
      <div className="bg-gradient-to-r from-teal-600 to-teal-800 rounded-xl shadow-lg overflow-hidden text-white p-8 relative">
        <div className="relative z-10 flex flex-col md:flex-row justify-between items-center md:items-start gap-6">
          <div className="flex items-center gap-6">
            <div className="h-24 w-24 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm border-2 border-white/50 text-3xl font-bold">
              {profile.full_name?.charAt(0) || user?.full_name?.charAt(0) || 'S'}
            </div>
            <div>
              <h1 className="text-3xl font-bold mb-1">Welcome back, {profile.full_name}!</h1>
              <p className="text-teal-100 flex items-center gap-2">
                <BookOpen size={16} /> 
                {profile.course_name} | Semester {profile.semester} | Section {profile.section}
              </p>
              <p className="text-teal-200 text-sm mt-1 flex items-center gap-2 mb-4">
                <User size={14} /> ID: {profile.roll_number} • {profile.email}
              </p>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => navigate('/my-profile/register-face')}
                className="bg-white/10 border-white/30 text-white hover:bg-white/20 flex items-center gap-2"
              >
                <Camera size={16} /> {profile.face_registered ? 'Update Face Registration' : 'Register Face for Attendance'}
              </Button>
            </div>
          </div>
          
          <div className="bg-white/10 p-4 rounded-lg backdrop-blur-md border border-white/20 text-center min-w-[150px]">
            <p className="text-teal-100 text-sm font-semibold uppercase tracking-wider mb-1">Overall Attendance</p>
            <div className="text-4xl font-bold flex items-baseline justify-center gap-1">
              {Math.round(s.attendance_percentage || 0)}<span className="text-xl">%</span>
            </div>
            {(s.attendance_percentage || 0) < 75 && (
              <div className="mt-2 text-xs bg-red-500/80 text-white py-1 px-2 rounded font-medium flex items-center justify-center gap-1">
                <AlertTriangle size={12} /> Low Attendance
              </div>
            )}
          </div>
        </div>
        
        {/* Decorative background circles */}
        <div className="absolute -top-24 -right-24 w-64 h-64 bg-teal-500 rounded-full mix-blend-multiply filter blur-3xl opacity-50"></div>
        <div className="absolute -bottom-24 -left-24 w-64 h-64 bg-teal-700 rounded-full mix-blend-multiply filter blur-3xl opacity-50"></div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="flex items-center gap-4 border-l-4 border-teal-500 hover:shadow-md transition-shadow">
          <div className="p-3 bg-teal-50 text-teal-600 rounded-lg"><CalendarCheck size={24} /></div>
          <div>
            <p className="text-sm text-gray-500 font-medium">Total Classes</p>
            <p className="text-2xl font-bold text-gray-800">{s.total_classes || 0}</p>
          </div>
        </Card>
        
        <Card className="flex items-center gap-4 border-l-4 border-green-500 hover:shadow-md transition-shadow">
          <div className="p-3 bg-green-50 text-green-600 rounded-lg"><CheckCircle size={24} /></div>
          <div>
            <p className="text-sm text-gray-500 font-medium">Present</p>
            <p className="text-2xl font-bold text-gray-800">{s.present}</p>
          </div>
        </Card>

        <Card className="flex items-center gap-4 border-l-4 border-yellow-500 hover:shadow-md transition-shadow">
          <div className="p-3 bg-yellow-50 text-yellow-600 rounded-lg"><Clock size={24} /></div>
          <div>
            <p className="text-sm text-gray-500 font-medium">Late</p>
            <p className="text-2xl font-bold text-gray-800">{s.late}</p>
          </div>
        </Card>
        
        <Card className="flex items-center gap-4 border-l-4 border-red-500 hover:shadow-md transition-shadow">
          <div className="p-3 bg-red-50 text-red-600 rounded-lg"><XCircle size={24} /></div>
          <div>
            <p className="text-sm text-gray-500 font-medium">Absent</p>
            <p className="text-2xl font-bold text-gray-800">{s.absent}</p>
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent History */}
        <div className="lg:col-span-2 space-y-6">
          <Card title="Recent Attendance Activity" className="h-full">
            {s.history && s.history.length > 0 ? (
              <div className="space-y-4 mt-4">
                {s.history.slice(0, 8).map((record, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 transition-colors">
                    <div className="flex items-center gap-3">
                      <div className={`w-2 h-2 rounded-full ${record.status === 'present' ? 'bg-green-500' : record.status === 'absent' ? 'bg-red-500' : 'bg-yellow-500'}`}></div>
                      <div>
                        <p className="font-semibold text-gray-800">{record.subject_name || record.subjectName || 'Unknown Subject'}</p>
                        <p className="text-xs text-gray-500">{new Date(record.date).toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'short', day: 'numeric' })} • {record.start_time || record.startTime}</p>
                      </div>
                    </div>
                    <Badge color={record.status === 'present' ? 'green' : record.status === 'absent' ? 'red' : 'yellow'}>
                      {record.status.toUpperCase()}
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <div className="py-12 flex flex-col items-center justify-center text-gray-400">
                <CalendarCheck size={48} className="mb-4 opacity-30" />
                <p>No recent attendance records found.</p>
              </div>
            )}
          </Card>
        </div>

        {/* Info & Notices */}
        <div className="space-y-6">
          <Card title="Face Recognition Status">
            <div className="mt-4 flex flex-col items-center text-center p-4 border rounded-lg bg-gray-50">
              <div className="w-16 h-16 bg-teal-100 text-teal-600 rounded-full flex items-center justify-center mb-3">
                <User size={32} />
              </div>
              <h3 className="font-bold text-gray-800">Biometric Profile</h3>
              {profile.face_registered ? (
                <div className="mt-2 text-sm text-green-600 font-medium flex items-center gap-1 bg-green-100 px-3 py-1 rounded-full">
                  <CheckCircle size={14} /> Registered and Active
                </div>
              ) : (
                <>
                  <div className="mt-2 text-sm text-amber-600 font-medium flex items-center gap-1 bg-amber-100 px-3 py-1 rounded-full mb-3">
                    <AlertTriangle size={14} /> Not Registered
                  </div>
                  <p className="text-xs text-gray-500">Contact your administrator to register your face for automated attendance.</p>
                </>
              )}
            </div>
          </Card>

          <Card title="System Notices" className="bg-teal-50 border-teal-100">
            <ul className="mt-2 space-y-3">
              <li className="flex gap-2 text-sm text-teal-800">
                <span className="mt-0.5">•</span>
                <span>You must maintain at least <strong>75%</strong> overall attendance to be eligible for final examinations.</span>
              </li>
              <li className="flex gap-2 text-sm text-teal-800">
                <span className="mt-0.5">•</span>
                <span>Marking is done automatically via cameras. If you are marked absent by mistake, contact your subject teacher within 24 hours.</span>
              </li>
            </ul>
          </Card>
        </div>
      </div>
    </div>
  );
}
