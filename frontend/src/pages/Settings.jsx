import React, { useState } from 'react';
import { Save } from 'lucide-react';
import { Button, Card } from '../components/common';
import toast from 'react-hot-toast';

import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function Settings() {
  const { user } = useAuth();
  if (user?.role === 'student') return <Navigate to="/my-profile" replace />;

  const [settings, setSettings] = useState({
    faceThreshold: 0.6,
    lowAttendanceThreshold: 75,
    lateThresholdMinutes: 15,
    enableLiveness: true,
    enableNotifications: true,
    systemName: 'AI Attendance Management System'
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setSettings(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSave = (e) => {
    e.preventDefault();
    toast.success('Settings saved successfully');
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">System Settings</h1>
      
      <Card>
        <form onSubmit={handleSave} className="space-y-6">
          <div className="space-y-4">
            <h2 className="text-lg font-semibold border-b pb-2">General</h2>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">System Name</label>
              <input type="text" name="systemName" value={settings.systemName} onChange={handleChange} className="w-full p-2 border rounded-md" />
            </div>
          </div>

          <div className="space-y-4">
            <h2 className="text-lg font-semibold border-b pb-2">Attendance Rules</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Low Attendance Alert Threshold (%)</label>
                <input type="number" name="lowAttendanceThreshold" value={settings.lowAttendanceThreshold} onChange={handleChange} className="w-full p-2 border rounded-md" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Late Mark Threshold (Minutes)</label>
                <input type="number" name="lateThresholdMinutes" value={settings.lateThresholdMinutes} onChange={handleChange} className="w-full p-2 border rounded-md" />
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <h2 className="text-lg font-semibold border-b pb-2">Face Recognition</h2>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Confidence Threshold: {settings.faceThreshold}</label>
              <input type="range" min="0.3" max="1.0" step="0.05" name="faceThreshold" value={settings.faceThreshold} onChange={handleChange} className="w-full" />
              <p className="text-xs text-gray-500 mt-1">Lower = More lenient, Higher = More strict</p>
            </div>
            <div className="flex items-center gap-2">
              <input type="checkbox" id="liveness" name="enableLiveness" checked={settings.enableLiveness} onChange={handleChange} className="w-4 h-4 text-indigo-600 rounded" />
              <label htmlFor="liveness" className="text-sm font-medium text-gray-700">Enable Liveness Detection (Anti-spoofing)</label>
            </div>
          </div>

          <div className="space-y-4">
            <h2 className="text-lg font-semibold border-b pb-2">Notifications</h2>
            <div className="flex items-center gap-2">
              <input type="checkbox" id="notif" name="enableNotifications" checked={settings.enableNotifications} onChange={handleChange} className="w-4 h-4 text-indigo-600 rounded" />
              <label htmlFor="notif" className="text-sm font-medium text-gray-700">Enable System Notifications</label>
            </div>
          </div>

          <div className="flex justify-end pt-4">
            <Button type="submit" className="flex items-center gap-2">
              <Save size={16} /> Save Settings
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
