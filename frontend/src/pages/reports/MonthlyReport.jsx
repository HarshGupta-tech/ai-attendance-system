import React, { useState, useEffect } from 'react';
import { Download } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import api from '../../utils/api';
import { Button, Card } from '../../components/common';

export default function MonthlyReport() {
  const [data, setData] = useState([]);
  const [month, setMonth] = useState(new Date().toISOString().slice(0, 7)); // YYYY-MM

  useEffect(() => {
    // Mock API fetch
    const mockData = Array.from({ length: 30 }, (_, i) => ({
      day: i + 1,
      present: Math.floor(Math.random() * 50) + 100,
      absent: Math.floor(Math.random() * 20) + 10
    }));
    setData(mockData);
  }, [month]);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Monthly Report</h1>
        <div className="flex gap-4">
          <input type="month" value={month} onChange={(e) => setMonth(e.target.value)} className="p-2 border rounded-md" />
          <Button variant="outline" className="flex items-center gap-2"><Download size={16} /> Export</Button>
        </div>
      </div>

      <Card className="h-96">
        <h2 className="text-lg font-semibold mb-4">Daily Attendance Overview</h2>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="day" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="present" stackId="a" fill="#10b981" name="Present" />
            <Bar dataKey="absent" stackId="a" fill="#ef4444" name="Absent" />
          </BarChart>
        </ResponsiveContainer>
      </Card>
    </div>
  );
}
