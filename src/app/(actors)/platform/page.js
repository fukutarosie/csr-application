'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Header from '../../components/Header';

export default function PlatformDashboard() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in and has Platform Management role
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');

    if (!token || !userData) {
      router.push('/');
      return;
    }

    const user = JSON.parse(userData);
    if (user.role.role_name !== 'Platform Management') {
      router.push('/');
      return;
    }

    setUser(user);
    setLoading(false);
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    router.push('/');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-100">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <Header title="Platform Management Dashboard" subtitle={`Welcome, ${user?.full_name}`} />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <div className="text-6xl mb-4">⚙️</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Platform Management Dashboard</h2>
          <p className="text-gray-600 mb-6">This is the dashboard for Platform Managers.</p>
          
          <div className="bg-blue-50 border-l-4 border-blue-400 p-4 rounded-lg text-left inline-block">
            <p className="text-sm text-gray-700">
              <strong>User Role:</strong> {user?.role.role_name}<br />
              <strong>Email:</strong> {user?.email}
            </p>
          </div>
        </div>

        {/* Feature Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-4xl mb-3">🖥️</div>
            <h3 className="font-bold text-lg mb-2">System Settings</h3>
            <p className="text-gray-600 text-sm">Configure platform settings</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-4xl mb-3">📊</div>
            <h3 className="font-bold text-lg mb-2">Analytics</h3>
            <p className="text-gray-600 text-sm">View platform analytics</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-4xl mb-3">🔒</div>
            <h3 className="font-bold text-lg mb-2">Security</h3>
            <p className="text-gray-600 text-sm">Manage security settings</p>
          </div>
        </div>
      </main>
    </div>
  );
}
