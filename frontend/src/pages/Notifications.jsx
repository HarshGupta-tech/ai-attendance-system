import React, { useState, useEffect } from 'react';
import { Bell, Info, AlertTriangle, CheckCircle, Clock } from 'lucide-react';
import api from '../utils/api';
import { Button, Card } from '../components/common';

export default function Notifications() {
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    api.get('/notifications').then(res => {
      setNotifications(res.data.items || res.data || []);
    }).catch(err => console.error(err));
  }, []);

  const markAllRead = () => {
    setNotifications(notifications.map(n => ({...n, read: true})));
  };

  const getIcon = (type) => {
    switch(type) {
      case 'warning': return <AlertTriangle className="text-yellow-500" />;
      case 'alert': return <AlertTriangle className="text-red-500" />;
      case 'success': return <CheckCircle className="text-green-500" />;
      default: return <Info className="text-blue-500" />;
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Notifications</h1>
        <Button variant="outline" onClick={markAllRead}>Mark all as read</Button>
      </div>

      <div className="space-y-4">
        {notifications.length === 0 ? (
          <Card className="text-center py-10 text-gray-500">No new notifications</Card>
        ) : (
          notifications.map(notif => (
            <Card key={notif.id} className={`flex items-start gap-4 p-4 ${!notif.read ? 'bg-blue-50/30 border-blue-100' : ''}`}>
              <div className="mt-1">{getIcon(notif.type)}</div>
              <div className="flex-1">
                <h3 className={`font-semibold ${!notif.read ? 'text-gray-900' : 'text-gray-700'}`}>{notif.title}</h3>
                <p className="text-gray-600 text-sm mt-1">{notif.message}</p>
                <div className="flex items-center gap-1 text-xs text-gray-400 mt-2">
                  <Clock size={12} /> {new Date(notif.createdAt).toLocaleString()}
                </div>
              </div>
              {!notif.read && <div className="w-2 h-2 rounded-full bg-blue-600 mt-2"></div>}
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
