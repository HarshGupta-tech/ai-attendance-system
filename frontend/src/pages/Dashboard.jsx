import React, { useState, useEffect } from 'react';
import { Users, UserCheck, UserX, Clock, Calendar } from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import StatsCard from '../components/common/StatsCard';
import Card from '../components/common/Card';
import Table from '../components/common/Table';
import Badge from '../components/common/Badge';
import { get } from '../utils/api';

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        const response = await get('/dashboard/statistics');
        const data = response.data;
        
        setStats({
          totalStudents: data.stats.total_students || 0,
          presentToday: data.stats.present_today || 0,
          absentToday: data.stats.absent_today || 0,
          lateToday: data.stats.late_today || 0,
          weeklyAttendance: data.daily_trend.map(d => ({
            name: new Date(d.date).toLocaleDateString('en-US', { weekday: 'short' }),
            present: d.present,
            absent: d.absent
          })),
          attendanceDistribution: [
            { name: 'Present', value: data.stats.present_today || 0 },
            { name: 'Absent', value: data.stats.absent_today || 0 },
            { name: 'Late', value: data.stats.late_today || 0 },
          ],
          lowAttendanceStudents: data.low_attendance_students.map(s => ({
            id: s.student_id,
            name: s.full_name,
            rollNo: s.student_code,
            attendance: `${s.attendance_percentage}%`,
            course: 'N/A'
          })),
          recentSessions: data.recent_sessions.map(s => ({
            id: s.session_id,
            subject: s.subject_name,
            time: s.time,
            attendance: '--',
            status: s.status === 'completed' ? 'Completed' : 'Ongoing'
          }))
        });
      } catch (error) {
        console.error('Failed to load dashboard data', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const COLORS = ['#10b981', '#ef4444', '#f59e0b'];

  const studentColumns = [
    { key: 'rollNo', label: 'Roll No' },
    { key: 'name', label: 'Name' },
    { key: 'course', label: 'Course' },
    { 
      key: 'attendance', 
      label: 'Attendance',
      render: (value) => (
        <Badge variant={parseInt(value) < 75 ? 'danger' : 'warning'}>{value}</Badge>
      )
    }
  ];

  const sessionColumns = [
    { key: 'subject', label: 'Subject' },
    { key: 'time', label: 'Time' },
    { key: 'attendance', label: 'Attendance' },
    { 
      key: 'status', 
      label: 'Status',
      render: (value) => (
        <Badge variant={value === 'Completed' ? 'success' : 'info'} showDot>
          {value}
        </Badge>
      )
    }
  ];

  if (loading || !stats) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 animate-pulse h-32"></div>
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 animate-pulse h-80"></div>
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 animate-pulse h-80"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Total Students"
          value={stats.totalStudents}
          icon={Users}
          iconBgColor="bg-blue-100"
          iconColor="text-blue-600"
        />
        <StatsCard
          title="Present Today"
          value={stats.presentToday}
          icon={UserCheck}
          iconBgColor="bg-green-100"
          iconColor="text-green-600"
          change="+5%"
          changeType="positive"
        />
        <StatsCard
          title="Absent Today"
          value={stats.absentToday}
          icon={UserX}
          iconBgColor="bg-red-100"
          iconColor="text-red-600"
          change="-2%"
          changeType="positive"
        />
        <StatsCard
          title="Late Today"
          value={stats.lateToday}
          icon={Clock}
          iconBgColor="bg-yellow-100"
          iconColor="text-yellow-600"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Daily Attendance (This Week)" icon={Calendar}>
          <div className="h-72 w-full mt-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats.weeklyAttendance} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
                <XAxis dataKey="name" axisLine={false} tickLine={false} />
                <YAxis axisLine={false} tickLine={false} />
                <Tooltip cursor={{ fill: '#f3f4f6' }} contentStyle={{ borderRadius: '0.5rem', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                <Legend iconType="circle" />
                <Bar dataKey="present" name="Present" fill="#10b981" radius={[4, 4, 0, 0]} maxBarSize={40} />
                <Bar dataKey="absent" name="Absent" fill="#ef4444" radius={[4, 4, 0, 0]} maxBarSize={40} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card title="Attendance Distribution (Today)">
          <div className="h-72 w-full mt-4 flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={stats.attendanceDistribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  fill="#8884d8"
                  paddingAngle={5}
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${percent ? (percent * 100).toFixed(0) : 0}%`}
                >
                  {stats.attendanceDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ borderRadius: '0.5rem', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Low Attendance Students" padding="none">
          <Table columns={studentColumns} data={stats.lowAttendanceStudents} />
        </Card>

        <Card title="Recent Sessions" padding="none">
          <Table columns={sessionColumns} data={stats.recentSessions} />
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
