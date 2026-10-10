import React, { useState, useEffect } from 'react';
import { Plus } from 'lucide-react';
import api from '../../utils/api';
import { Button, Card, Badge, LoadingSpinner } from '../../components/common';

export default function UserList() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/users').then(res => {
      setUsers(res.data.items || res.data || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const getRoleColor = (role) => {
    switch(role) {
      case 'admin': return 'red';
      case 'teacher': return 'blue';
      case 'staff': return 'green';
      default: return 'gray';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">User Management</h1>
        <Button className="flex items-center gap-2"><Plus size={16} /> Add User</Button>
      </div>

      <Card>
        {loading ? <LoadingSpinner /> : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b bg-gray-50 text-gray-600 text-sm">
                  <th className="p-4">Username</th>
                  <th className="p-4">Full Name</th>
                  <th className="p-4">Email</th>
                  <th className="p-4">Role</th>
                  <th className="p-4">Status</th>
                </tr>
              </thead>
              <tbody>
                {users.map(user => (
                  <tr key={user.id} className="border-b hover:bg-gray-50">
                    <td className="p-4 font-medium">{user.username}</td>
                    <td className="p-4">{user.fullName}</td>
                    <td className="p-4">{user.email}</td>
                    <td className="p-4"><Badge color={getRoleColor(user.role)}>{user.role}</Badge></td>
                    <td className="p-4"><Badge color={user.isActive !== false ? 'green' : 'red'}>{user.isActive !== false ? 'Active' : 'Disabled'}</Badge></td>
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
