'use client';

import { useRouter } from 'next/navigation';
import axios from 'axios';

export default function Header({ title = 'Dashboard', subtitle = null }) {
  const router = useRouter();

  const getToken = () => localStorage.getItem('token');

  const handleLogout = async () => {
    try {
      await axios.post('http://localhost:5000/api/auth/logout', {}, {
        headers: {
          'Authorization': `Bearer ${getToken()}`
        }
      });
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      // Clear token and user from localStorage regardless of API response
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      router.push('/');
    }
  };

  return (
    <header className="bg-white shadow">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{title}</h1>
          {subtitle && <p className="text-gray-600 mt-2">{subtitle}</p>}
        </div>
        <button
          onClick={handleLogout}
          className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
        >
          Logout
        </button>
      </div>
    </header>
  );
}
