import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import api from '../../utils/api';
import { Button, Card, Input } from '../../components/common';
import toast from 'react-hot-toast';

export default function StudentForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEdit = Boolean(id);
  
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(isEdit);
  const [courses, setCourses] = useState([]);
  const [departments, setDepartments] = useState([]);
  
  const [formData, setFormData] = useState({
    studentId: '',
    rollNumber: '',
    fullName: '',
    email: '',
    phone: '',
    course: '',
    department: '',
    semester: '1',
    section: '',
    dateOfAdmission: '',
    status: 'active'
  });

  useEffect(() => {
    const fetchOptions = async () => {
      try {
        const [courseRes, deptRes] = await Promise.all([
          api.get('/options/courses'),
          api.get('/options/departments')
        ]);
        setCourses(courseRes.data || []);
        setDepartments(deptRes.data || []);
      } catch (err) {
        // Fallback options for UI
        setCourses([{ id: 'BTECH', name: 'B.Tech' }, { id: 'MTECH', name: 'M.Tech' }]);
        setDepartments([{ id: 'CSE', name: 'Computer Science' }, { id: 'ECE', name: 'Electronics' }]);
      }
    };
    fetchOptions();

    if (isEdit) {
      const fetchStudent = async () => {
        try {
          const res = await api.get(`/students/${id}`);
          setFormData(res.data);
        } catch (err) {
          toast.error('Failed to load student data');
          navigate('/students');
        } finally {
          setFetching(false);
        }
      };
      fetchStudent();
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
        await api.put(`/students/${id}`, formData);
        toast.success('Student updated successfully');
      } else {
        await api.post('/students', formData);
        toast.success('Student added successfully');
      }
      navigate('/students');
    } catch (err) {
      toast.error(err.response?.data?.message || 'Error saving student');
    } finally {
      setLoading(false);
    }
  };

  if (fetching) return <div>Loading...</div>;

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">{isEdit ? 'Edit Student' : 'Add Student'}</h1>
      </div>

      <Card>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Student ID</label>
              <input required type="text" name="studentId" value={formData.studentId} onChange={handleChange} className="w-full p-2 border rounded-md" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Roll Number</label>
              <input required type="text" name="rollNumber" value={formData.rollNumber} onChange={handleChange} className="w-full p-2 border rounded-md" />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
              <input required type="text" name="fullName" value={formData.fullName} onChange={handleChange} className="w-full p-2 border rounded-md" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input required type="email" name="email" value={formData.email} onChange={handleChange} className="w-full p-2 border rounded-md" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
              <input type="text" name="phone" value={formData.phone} onChange={handleChange} className="w-full p-2 border rounded-md" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Department</label>
              <select required name="department" value={formData.department} onChange={handleChange} className="w-full p-2 border rounded-md bg-white">
                <option value="">Select Department</option>
                {departments.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Course</label>
              <select required name="course" value={formData.course} onChange={handleChange} className="w-full p-2 border rounded-md bg-white">
                <option value="">Select Course</option>
                {courses.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Semester</label>
              <select required name="semester" value={formData.semester} onChange={handleChange} className="w-full p-2 border rounded-md bg-white">
                {[...Array(10)].map((_, i) => (
                  <option key={i+1} value={i+1}>{i+1}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Section</label>
              <input type="text" name="section" value={formData.section} onChange={handleChange} className="w-full p-2 border rounded-md" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Date of Admission</label>
              <input type="date" name="dateOfAdmission" value={formData.dateOfAdmission} onChange={handleChange} className="w-full p-2 border rounded-md" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <select name="status" value={formData.status} onChange={handleChange} className="w-full p-2 border rounded-md bg-white">
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="suspended">Suspended</option>
              </select>
            </div>
          </div>
          
          <div className="flex justify-end gap-4 pt-4 border-t">
            <Button type="button" variant="outline" onClick={() => navigate('/students')} disabled={loading}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Saving...' : 'Save Student'}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
