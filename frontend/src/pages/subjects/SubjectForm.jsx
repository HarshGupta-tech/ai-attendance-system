import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import api from '../../utils/api';
import { Button, Card } from '../../components/common';
import toast from 'react-hot-toast';

export default function SubjectForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEdit = Boolean(id);
  
  const [loading, setLoading] = useState(false);
  const [teachers, setTeachers] = useState([]);
  
  const [formData, setFormData] = useState({
    code: '',
    name: '',
    course: '',
    department: '',
    semester: '1',
    credits: '3',
    teacherId: '',
    status: 'active'
  });

  useEffect(() => {
    // Fetch teachers
    api.get('/users?role=teacher').then(res => {
      setTeachers(res.data.items || res.data || []);
    }).catch(err => console.error(err));

    if (isEdit) {
      api.get(`/subjects/${id}`).then(res => {
        setFormData(res.data);
      }).catch(err => {
        toast.error('Failed to load subject data');
        navigate('/subjects');
      });
    }
  }, [id, isEdit, navigate]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (isEdit) {
        await api.put(`/subjects/${id}`, formData);
        toast.success('Subject updated');
      } else {
        await api.post('/subjects', formData);
        toast.success('Subject added');
      }
      navigate('/subjects');
    } catch (err) {
      toast.error('Error saving subject');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">{isEdit ? 'Edit Subject' : 'Add Subject'}</h1>

      <Card>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Subject Code</label>
              <input required type="text" name="code" value={formData.code} onChange={handleChange} className="w-full p-2 border rounded-md" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Subject Name</label>
              <input required type="text" name="name" value={formData.name} onChange={handleChange} className="w-full p-2 border rounded-md" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Course</label>
              <input required type="text" name="course" value={formData.course} onChange={handleChange} className="w-full p-2 border rounded-md" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Department</label>
              <input required type="text" name="department" value={formData.department} onChange={handleChange} className="w-full p-2 border rounded-md" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Semester</label>
              <select required name="semester" value={formData.semester} onChange={handleChange} className="w-full p-2 border rounded-md bg-white">
                {[...Array(10)].map((_, i) => <option key={i+1} value={i+1}>{i+1}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Credits</label>
              <input required type="number" min="1" max="6" name="credits" value={formData.credits} onChange={handleChange} className="w-full p-2 border rounded-md" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Assigned Teacher</label>
              <select name="teacherId" value={formData.teacherId} onChange={handleChange} className="w-full p-2 border rounded-md bg-white">
                <option value="">Select Teacher</option>
                {teachers.map(t => <option key={t.id} value={t.id}>{t.fullName}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <select name="status" value={formData.status} onChange={handleChange} className="w-full p-2 border rounded-md bg-white">
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>
          </div>
          
          <div className="flex justify-end gap-4 pt-4 border-t">
            <Button type="button" variant="outline" onClick={() => navigate('/subjects')} disabled={loading}>Cancel</Button>
            <Button type="submit" disabled={loading}>{loading ? 'Saving...' : 'Save Subject'}</Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
