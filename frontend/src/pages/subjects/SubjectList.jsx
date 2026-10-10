import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Edit, Trash2 } from 'lucide-react';
import api from '../../utils/api';
import { Button, Card, Badge, LoadingSpinner, ConfirmDialog } from '../../components/common';
import toast from 'react-hot-toast';

export default function SubjectList() {
  const navigate = useNavigate();
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showDelete, setShowDelete] = useState(null);

  const fetchSubjects = async () => {
    try {
      setLoading(true);
      const res = await api.get('/subjects');
      setSubjects(res.data.items || res.data || []);
    } catch (err) {
      toast.error('Failed to load subjects');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSubjects();
  }, []);

  const handleDelete = async () => {
    try {
      await api.del(`/subjects/${showDelete}`);
      toast.success('Subject deleted');
      setSubjects(subjects.filter(s => s.id !== showDelete));
      setShowDelete(null);
    } catch (err) {
      toast.error('Failed to delete subject');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Subjects</h1>
        <Button onClick={() => navigate('/subjects/add')} className="flex items-center gap-2">
          <Plus size={16} /> Add Subject
        </Button>
      </div>

      <Card>
        {loading ? (
          <LoadingSpinner />
        ) : subjects.length === 0 ? (
          <div className="text-center py-10 text-gray-500">No subjects found. Create one to get started.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b bg-gray-50 text-gray-600 text-sm">
                  <th className="p-4">Code</th>
                  <th className="p-4">Name</th>
                  <th className="p-4">Course</th>
                  <th className="p-4">Semester</th>
                  <th className="p-4">Credits</th>
                  <th className="p-4">Teacher</th>
                  <th className="p-4">Status</th>
                  <th className="p-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {subjects.map((subject) => (
                  <tr key={subject.id} className="border-b hover:bg-gray-50">
                    <td className="p-4 font-medium">{subject.code}</td>
                    <td className="p-4">{subject.name}</td>
                    <td className="p-4">{subject.course}</td>
                    <td className="p-4">{subject.semester}</td>
                    <td className="p-4">{subject.credits}</td>
                    <td className="p-4">{subject.teacherName || 'Not Assigned'}</td>
                    <td className="p-4">
                      <Badge color={subject.status === 'active' ? 'green' : 'gray'}>
                        {subject.status || 'Active'}
                      </Badge>
                    </td>
                    <td className="p-4 text-right space-x-2">
                      <Button variant="ghost" size="sm" onClick={() => navigate(`/subjects/${subject.id}/edit`)}><Edit size={16} /></Button>
                      <Button variant="ghost" size="sm" className="text-red-600" onClick={() => setShowDelete(subject.id)}><Trash2 size={16} /></Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {showDelete && (
        <ConfirmDialog
          title="Delete Subject"
          message="Are you sure you want to delete this subject? This may affect attendance records."
          onConfirm={handleDelete}
          onCancel={() => setShowDelete(null)}
        />
      )}
    </div>
  );
}
