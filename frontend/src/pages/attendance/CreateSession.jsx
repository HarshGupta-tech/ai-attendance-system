import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../utils/api';
import { Button, Card } from '../../components/common';
import toast from 'react-hot-toast';

export default function CreateSession() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [subjects, setSubjects] = useState([]);
  
  const today = new Date().toISOString().split('T')[0];
  const now = new Date().toTimeString().slice(0,5);

  const [formData, setFormData] = useState({
    subjectId: '',
    date: today,
    startTime: now,
    endTime: '',
    lateThreshold: 15,
    course: '',
    semester: '',
    section: ''
  });

  useEffect(() => {
    api.get('/subjects').then(res => {
      setSubjects(res.data.items || res.data || []);
    });
  }, []);

  const handleSubjectChange = (e) => {
    const subjectId = e.target.value;
    const subject = subjects.find(s => s.id === parseInt(subjectId));
    if (subject) {
      setFormData(prev => ({
        ...prev,
        subjectId,
        course: subject.course || prev.course,
        semester: subject.semester || prev.semester
      }));
    } else {
      setFormData(prev => ({ ...prev, subjectId }));
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    const payload = {
      subject_id: parseInt(formData.subjectId),
      date: formData.date,
      start_time: formData.startTime,
      end_time: formData.endTime,
      late_threshold_minutes: parseInt(formData.lateThreshold),
      semester: formData.semester ? parseInt(formData.semester) : null,
      section: formData.section || null,
    };
    
    try {
      const res = await api.post('/attendance/session', payload);
      toast.success('Session created successfully');
      navigate(`/attendance/session/${res.data.id || res.data.sessionId}`);
    } catch (err) {
      toast.error('Failed to create session');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Create Attendance Session</h1>

      <Card>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Subject</label>
            <select required name="subjectId" value={formData.subjectId} onChange={handleSubjectChange} className="w-full p-2 border rounded-md bg-white">
              <option value="">Select Subject</option>
              {subjects.map(s => <option key={s.id} value={s.id}>{s.name} ({s.code})</option>)}
            </select>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Course</label>
              <input required type="text" name="course" value={formData.course} onChange={handleChange} className="w-full p-2 border rounded-md bg-gray-50" readOnly />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Semester</label>
              <input required type="text" name="semester" value={formData.semester} onChange={handleChange} className="w-full p-2 border rounded-md bg-gray-50" readOnly />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Section</label>
              <input required type="text" name="section" value={formData.section} onChange={handleChange} placeholder="e.g. A" className="w-full p-2 border rounded-md" />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Date</label>
              <input required type="date" name="date" value={formData.date} onChange={handleChange} className="w-full p-2 border rounded-md" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Late Threshold (minutes)</label>
              <input required type="number" min="0" name="lateThreshold" value={formData.lateThreshold} onChange={handleChange} className="w-full p-2 border rounded-md" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Start Time</label>
              <input required type="time" name="startTime" value={formData.startTime} onChange={handleChange} className="w-full p-2 border rounded-md" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">End Time</label>
              <input required type="time" name="endTime" value={formData.endTime} onChange={handleChange} className="w-full p-2 border rounded-md" />
            </div>
          </div>
          
          <div className="flex justify-end gap-4 pt-4 border-t">
            <Button type="button" variant="outline" onClick={() => navigate('/attendance')} disabled={loading}>Cancel</Button>
            <Button type="submit" disabled={loading}>{loading ? 'Creating...' : 'Create Session'}</Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
