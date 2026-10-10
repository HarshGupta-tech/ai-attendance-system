import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Plus, Eye, Edit, Camera, Search, Filter } from 'lucide-react';
import api from '../../utils/api';
import { Button, Card, Table, Badge, LoadingSpinner, EmptyState, Pagination } from '../../components/common';
import toast from 'react-hot-toast';

export default function StudentList() {
  const navigate = useNavigate();
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const fetchStudents = async () => {
    try {
      setLoading(true);
      const res = await api.get(`/students?page=${page}&search=${searchTerm}`);
      setStudents(res.data.items || res.data || []);
      setTotalPages(res.data.totalPages || 1);
    } catch (err) {
      toast.error('Failed to load students');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const delayDebounceFn = setTimeout(() => {
      fetchStudents();
    }, 300);
    return () => clearTimeout(delayDebounceFn);
  }, [searchTerm, page]);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Students</h1>
        <Button onClick={() => navigate('/students/add')} className="flex items-center gap-2">
          <Plus size={16} /> Add Student
        </Button>
      </div>

      <Card>
        <div className="flex gap-4 mb-6">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Search by name, ID, or roll number..."
              className="w-full pl-10 pr-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <Button variant="outline" className="flex items-center gap-2">
            <Filter size={16} /> Filters
          </Button>
        </div>

        {loading ? (
          <LoadingSpinner />
        ) : students.length === 0 ? (
          <EmptyState title="No students found" message="Try adjusting your search or add a new student." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b bg-gray-50 text-gray-600 text-sm">
                  <th className="p-4">Student ID</th>
                  <th className="p-4">Name</th>
                  <th className="p-4">Roll Number</th>
                  <th className="p-4">Course</th>
                  <th className="p-4">Sem/Sec</th>
                  <th className="p-4">Status</th>
                  <th className="p-4">Face Reg.</th>
                  <th className="p-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {students.map((student) => (
                  <tr key={student.id} className="border-b hover:bg-gray-50 cursor-pointer" onClick={() => navigate(`/students/${student.id}`)}>
                    <td className="p-4">{student.studentId}</td>
                    <td className="p-4 font-medium">{student.fullName}</td>
                    <td className="p-4">{student.rollNumber}</td>
                    <td className="p-4">{student.course}</td>
                    <td className="p-4">{student.semester} / {student.section}</td>
                    <td className="p-4">
                      <Badge color={student.status === 'active' ? 'green' : student.status === 'suspended' ? 'red' : 'gray'}>
                        {student.status}
                      </Badge>
                    </td>
                    <td className="p-4">
                      <span className={student.faceRegistered ? 'text-green-600 font-bold' : 'text-red-600 font-bold'}>
                        {student.faceRegistered ? '✓' : '✗'}
                      </span>
                    </td>
                    <td className="p-4 text-right space-x-2" onClick={e => e.stopPropagation()}>
                      <Button variant="ghost" size="sm" onClick={() => navigate(`/students/${student.id}`)}><Eye size={16} /></Button>
                      <Button variant="ghost" size="sm" onClick={() => navigate(`/students/${student.id}/edit`)}><Edit size={16} /></Button>
                      <Button variant="ghost" size="sm" onClick={() => navigate(`/students/${student.id}/register-face`)}><Camera size={16} /></Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="mt-4 flex justify-end">
               <Pagination currentPage={page} totalPages={totalPages} onPageChange={setPage} />
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}
