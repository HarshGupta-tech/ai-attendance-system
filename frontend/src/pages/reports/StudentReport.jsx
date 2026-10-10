import React, { useState, useEffect } from 'react';
import { Download, Search } from 'lucide-react';
import api from '../../utils/api';
import { Button, Card, Badge, LoadingSpinner } from '../../components/common';

export default function StudentReport() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({ studentId: '', startDate: '', endDate: '' });

  const fetchReport = async () => {
    setLoading(true);
    try {
      const query = new URLSearchParams(filters).toString();
      const res = await api.get(`/reports/student?${query}`);
      // Mock data if empty
      setData(res.data.length ? res.data : [
        { id: '1', studentId: 'S001', name: 'John Doe', totalClasses: 40, present: 32, late: 2, absent: 6, percentage: 80 },
        { id: '2', studentId: 'S002', name: 'Jane Smith', totalClasses: 40, present: 22, late: 4, absent: 14, percentage: 55 }
      ]);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReport();
  }, []); // Run once, then on search

  const handleExport = (type) => {
    // Implement export via API
    window.open(`/api/reports/export/${type}?type=student`, '_blank');
  };

  const getRiskLevel = (pct) => {
    if (pct >= 75) return { label: 'Safe', color: 'green' };
    if (pct >= 60) return { label: 'Warning', color: 'yellow' };
    return { label: 'Critical', color: 'red' };
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <h1 className="text-2xl font-bold text-gray-900">Student Attendance Report</h1>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => handleExport('csv')} className="flex items-center gap-2"><Download size={16} /> CSV</Button>
          <Button variant="outline" onClick={() => handleExport('pdf')} className="flex items-center gap-2"><Download size={16} /> PDF</Button>
        </div>
      </div>

      <Card className="flex flex-wrap gap-4 items-end">
        <div className="flex-1 min-w-[200px]">
          <label className="block text-sm font-medium text-gray-700 mb-1">Student ID or Name</label>
          <input type="text" className="w-full p-2 border rounded-md" value={filters.studentId} onChange={(e) => setFilters({...filters, studentId: e.target.value})} placeholder="Search..." />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">From Date</label>
          <input type="date" className="w-full p-2 border rounded-md" value={filters.startDate} onChange={(e) => setFilters({...filters, startDate: e.target.value})} />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">To Date</label>
          <input type="date" className="w-full p-2 border rounded-md" value={filters.endDate} onChange={(e) => setFilters({...filters, endDate: e.target.value})} />
        </div>
        <Button onClick={fetchReport} className="flex items-center gap-2"><Search size={16} /> Generate</Button>
      </Card>

      <Card>
        {loading ? <LoadingSpinner /> : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b bg-gray-50 text-gray-600 text-sm">
                  <th className="p-4">Student</th>
                  <th className="p-4 text-center">Classes</th>
                  <th className="p-4 text-center">Present</th>
                  <th className="p-4 text-center">Late</th>
                  <th className="p-4 text-center">Absent</th>
                  <th className="p-4">Attendance %</th>
                  <th className="p-4 text-center">Risk Level</th>
                </tr>
              </thead>
              <tbody>
                {data.map((row) => {
                  const risk = getRiskLevel(row.percentage);
                  return (
                    <tr key={row.id} className="border-b hover:bg-gray-50">
                      <td className="p-4">
                        <div className="font-medium">{row.name}</div>
                        <div className="text-xs text-gray-500">{row.studentId}</div>
                      </td>
                      <td className="p-4 text-center">{row.totalClasses}</td>
                      <td className="p-4 text-center text-green-600">{row.present}</td>
                      <td className="p-4 text-center text-yellow-600">{row.late}</td>
                      <td className="p-4 text-center text-red-600">{row.absent}</td>
                      <td className="p-4 min-w-[150px]">
                        <div className="flex items-center gap-2">
                          <span className="w-8 font-medium">{row.percentage}%</span>
                          <div className="flex-1 bg-gray-200 rounded-full h-2">
                            <div className={`h-2 rounded-full bg-${risk.color}-500`} style={{ width: `${row.percentage}%` }}></div>
                          </div>
                        </div>
                      </td>
                      <td className="p-4 text-center">
                        <Badge color={risk.color}>{risk.label}</Badge>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
