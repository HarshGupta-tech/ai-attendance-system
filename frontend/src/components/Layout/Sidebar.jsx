import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import {
  GraduationCap,
  LayoutDashboard,
  Users,
  BookOpen,
  ClipboardCheck,
  FileText,
  UserCog,
  Bell,
  Settings,
  Shield,
  LogOut,
  UserCircle,
} from 'lucide-react';

const Sidebar = ({ isMobileOpen, closeMobileSidebar }) => {
  const { user, logout, hasRole } = useAuth();
  const location = useLocation();

  // Build nav items based on role
  let navItems = [];

  if (user?.role === 'student') {
    // Student sees only their own stuff
    navItems = [
      { name: 'My Profile', path: '/my-profile', icon: UserCircle },
      { name: 'Mark Attendance', path: '/my-profile/mark-attendance', icon: ClipboardCheck },
      { name: 'Notifications', path: '/notifications', icon: Bell },
    ];
  } else {
    // Admin / Teacher sees the full menu
    navItems = [
      { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
      { name: 'Students', path: '/students', icon: Users },
      { name: 'Subjects', path: '/subjects', icon: BookOpen },
      { name: 'Attendance', path: '/attendance', icon: ClipboardCheck },
      { name: 'Reports', path: '/reports', icon: FileText },
      { name: 'Notifications', path: '/notifications', icon: Bell },
      { name: 'Settings', path: '/settings', icon: Settings },
    ];

    if (hasRole(['admin', 'super_admin'])) {
      navItems.splice(5, 0, { name: 'Users', path: '/users', icon: UserCog });
      navItems.push({ name: 'Audit Logs', path: '/audit-logs', icon: Shield });
    }
  }

  const isStudent = user?.role === 'student';
  const bgClass = isStudent ? 'bg-teal-900' : 'bg-indigo-900';
  const hoverClass = isStudent ? 'hover:bg-teal-800' : 'hover:bg-indigo-800';
  const activeClass = isStudent ? 'bg-teal-800 text-white' : 'bg-indigo-800 text-white';
  const textMutedClass = isStudent ? 'text-teal-100' : 'text-indigo-100';
  const textIconClass = isStudent ? 'text-teal-300' : 'text-indigo-300';
  const borderClass = isStudent ? 'border-teal-800' : 'border-indigo-800';
  const iconBgClass = isStudent ? 'bg-teal-700' : 'bg-indigo-700';

  const baseClasses = `fixed inset-y-0 left-0 z-50 w-64 ${bgClass} text-white transition-transform duration-300 ease-in-out md:translate-x-0 md:static md:inset-0 flex flex-col`;
  const mobileClasses = isMobileOpen ? "translate-x-0" : "-translate-x-full";

  return (
    <>
      {isMobileOpen && (
        <div
          className="fixed inset-0 bg-gray-900 bg-opacity-50 z-40 md:hidden"
          onClick={closeMobileSidebar}
        ></div>
      )}
      <div className={`${baseClasses} ${mobileClasses}`}>
        {/* Logo */}
        <div className={`flex items-center justify-center h-16 border-b ${borderClass}`}>
          <GraduationCap className={`h-8 w-8 ${textIconClass} mr-2`} />
          <span className="text-xl font-bold tracking-wider">AI Attendance</span>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path || (item.path !== '/' && location.pathname.startsWith(item.path));

            return (
              <NavLink
                key={item.name}
                to={item.path}
                onClick={() => isMobileOpen && closeMobileSidebar()}
                className={`flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors duration-150 ${
                  isActive
                    ? activeClass
                    : `${textMutedClass} ${hoverClass} hover:text-white`
                }`}
              >
                <Icon className={`h-5 w-5 mr-3 ${isActive ? 'text-white' : textIconClass}`} />
                {item.name}
              </NavLink>
            );
          })}
        </nav>

        {/* User profile & Logout */}
        <div className={`p-4 border-t ${borderClass}`}>
          <div className="flex items-center mb-4">
            <div className={`h-10 w-10 rounded-full ${iconBgClass} flex items-center justify-center text-white font-bold`}>
              {user?.full_name?.charAt(0) || 'U'}
            </div>
            <div className="ml-3 truncate">
              <p className="text-sm font-medium text-white truncate">{user?.full_name || 'User'}</p>
              <p className={`text-xs ${textIconClass} capitalize`}>{user?.role || 'Role'}</p>
            </div>
          </div>
          <button
            onClick={logout}
            className={`flex items-center w-full px-4 py-2 text-sm font-medium ${textMutedClass} rounded-lg ${hoverClass} hover:text-white transition-colors`}
          >
            <LogOut className={`h-5 w-5 mr-3 ${textIconClass}`} />
            Logout
          </button>
        </div>
      </div>
    </>
  );
};

export default Sidebar;