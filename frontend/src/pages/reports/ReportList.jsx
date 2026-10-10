import React from 'react';
import { useNavigate } from 'react-router-dom';
import { User, BookOpen, Calendar, AlertTriangle } from 'lucide-react';
import { Card } from '../../components/common';

export default function ReportList() {
  const navigate = useNavigate();

  const reports = [
    {
      title: 'Student Attendance Report',
      description: 'View detailed attendance history and statistics for individual students.',
      icon: <User size={32} className="text-indigo-600" />,
      path: '/reports/student',
      color: 'bg-indigo-50 border-indigo-100'
    },
    {
      title: 'Subject Attendance Report',
      description: 'Analyze overall attendance trends and statistics across different subjects.',
      icon: <BookOpen size={32} className="text-blue-600" />,
      path: '/reports/subject',
      color: 'bg-blue-50 border-blue-100'
    },
    {
      title: 'Monthly Report',
      description: 'Get a comprehensive view of daily attendance across the entire month.',
      icon: <Calendar size={32} className="text-emerald-600" />,
      path: '/reports/monthly',
      color: 'bg-emerald-50 border-emerald-100'
    },
    {
      title: 'Low Attendance Report',
      description: 'Identify students at risk with attendance below the required threshold.',
      icon: <AlertTriangle size={32} className="text-red-600" />,
      path: '/reports/low-attendance', // optional or map to another page
      color: 'bg-red-50 border-red-100'
    }
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Reports Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
        {reports.map((report, idx) => (
          <Card 
            key={idx} 
            className={`cursor-pointer hover:shadow-md transition-shadow border-2 ${report.color}`}
            onClick={() => navigate(report.path)}
          >
            <div className="flex items-start gap-4 p-2">
              <div className="p-3 bg-white rounded-lg shadow-sm">
                {report.icon}
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-1">{report.title}</h3>
                <p className="text-gray-600">{report.description}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
