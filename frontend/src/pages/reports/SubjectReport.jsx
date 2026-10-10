import React, { useState, useEffect } from 'react';
import { Download } from 'lucide-react';
import api from '../../utils/api';
import { Button, Card, LoadingSpinner } from '../../components/common';

export default function SubjectReport() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchReport = async () => {
      setLoading(true);
      try {
        const res = await api.get(`/reports/subject`);
        // Mock data fallback
        setData(res.data.length ? res.data : [
          { id: '1', code: 'CS101', name: 'Intro to Programming', totalSessions: 24, avgAttendance: 85, highest: 100, lowest: 45 },
          { id: '2', code: 'CS102', name: 'Data Structures', totalSessions: 22, avgAttendance: 72, highest: 95, lowest: 30 }
        ]);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchReport();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Subject Attendance Report</h1>
        <Button variant="outline" className="flex items-center gap-2"><Download size={16} /> Export CSV</Button>
      </div>

      <Card>
        {loading ? <LoadingSpinner /> : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b bg-gray-50 text-gray-600 text-sm">
                  <th className="p-4">Subject</th>
                  <th className="p-4 text-center">Total Sessions</th>
                  <th className="p-4 text-center">Avg Attendance</th>
                  <th className="p-4 text-center">Highest</th>
                  <th className="p-4 text-center">Lowest</th>
                </tr>
              </thead>
              <tbody>
                {data.map((row) => (
                  <tr key={row.id} className="border-b hover:bg-gray-50">
                    <td className="p-4">
                      <div className="font-medium">{row.name}</div>
                      <div className="text-xs text-gray-500">{row.code}</div>
                    </td>
                    <td className="p-4 text-center">{row.totalSessions}</td>
                    <td className="p-4 text-center font-semibold text-indigo-600">{row.avgAttendance}%</td>
                    <td className="p-4 text-center text-green-600">{row.highest}%</td>
                    <td className="p-4 text-center text-red-600">{row.lowest}%</td>
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
