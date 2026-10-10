import React, { useState, useEffect } from 'react';
import api from '../utils/api';
import { Card, Badge, LoadingSpinner, Pagination } from '../components/common';

export default function AuditLogs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);

  useEffect(() => {
    // Mock data for audit logs
    const mockLogs = [
      { id: 1, timestamp: new Date().toISOString(), user: 'admin', action: 'CREATE', resource: 'Student', details: 'Added John Doe', ip: '192.168.1.1' },
      { id: 2, timestamp: new Date(Date.now() - 3600000).toISOString(), user: 'teacher1', action: 'UPDATE', resource: 'Attendance', details: 'Modified session #45', ip: '192.168.1.5' },
      { id: 3, timestamp: new Date(Date.now() - 7200000).toISOString(), user: 'admin', action: 'DELETE', resource: 'Subject', details: 'Removed PHY101', ip: '192.168.1.1' }
    ];
    setLogs(mockLogs);
    setLoading(false);
  }, [page]);

  const getActionColor = (action) => {
    switch(action) {
      case 'CREATE': return 'green';
      case 'UPDATE': return 'blue';
      case 'DELETE': return 'red';
      default: return 'gray';
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Audit Logs</h1>
      
      <Card>
        {loading ? <LoadingSpinner /> : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b bg-gray-50 text-gray-600 text-sm">
                  <th className="p-4">Timestamp</th>
                  <th className="p-4">User</th>
                  <th className="p-4">Action</th>
                  <th className="p-4">Resource</th>
                  <th className="p-4">Details</th>
                  <th className="p-4">IP Address</th>
                </tr>
              </thead>
              <tbody>
                {logs.map(log => (
                  <tr key={log.id} className="border-b hover:bg-gray-50 text-sm">
                    <td className="p-4 whitespace-nowrap text-gray-500">{new Date(log.timestamp).toLocaleString()}</td>
                    <td className="p-4 font-medium">{log.user}</td>
                    <td className="p-4"><Badge color={getActionColor(log.action)}>{log.action}</Badge></td>
                    <td className="p-4">{log.resource}</td>
                    <td className="p-4">{log.details}</td>
                    <td className="p-4 text-gray-500 font-mono text-xs">{log.ip}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="mt-4 flex justify-end">
               <Pagination currentPage={page} totalPages={5} onPageChange={setPage} />
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}
