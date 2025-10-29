'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import Link from 'next/link';

export default function PINDashboard() {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterStatus, setFilterStatus] = useState('ACTIVE');
  const [stats, setStats] = useState({
    total: 0,
    active: 0,
    suspended: 0,
    fulfilled: 0,
  });

  useEffect(() => {
    fetchRequests();
  }, [filterStatus]);

  const fetchRequests = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      if (!token) {
        setError('Not authenticated');
        return;
      }

      const response = await axios.get(
        `http://localhost:5000/api/requests?status=${filterStatus}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.data.success) {
        setRequests(response.data.data || []);
        
        // Calculate stats
        setStats({
          total: response.data.count || 0,
          active: response.data.data?.filter(r => r.status === 'ACTIVE').length || 0,
          suspended: response.data.data?.filter(r => r.status === 'SUSPENDED').length || 0,
          fulfilled: response.data.data?.filter(r => r.status === 'FULFILLED').length || 0,
        });
      } else {
        setError(response.data.message);
      }
    } catch (err) {
      setError(err.message);
      console.error('Error fetching requests:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const colors = {
      ACTIVE: 'bg-green-100 text-green-800',
      SUSPENDED: 'bg-yellow-100 text-yellow-800',
      FULFILLED: 'bg-blue-100 text-blue-800',
      CANCELLED: 'bg-red-100 text-red-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getPriorityBadge = (priority) => {
    const colors = {
      LOW: 'bg-blue-50 text-blue-700 border border-blue-200',
      MEDIUM: 'bg-yellow-50 text-yellow-700 border border-yellow-200',
      HIGH: 'bg-orange-50 text-orange-700 border border-orange-200',
      URGENT: 'bg-red-50 text-red-700 border border-red-200',
    };
    return colors[priority] || 'bg-gray-50 text-gray-700';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-bold text-gray-800">PIN Dashboard</h1>
            <p className="text-gray-600 mt-2">Manage your service requests</p>
          </div>
          <Link href="/pin/request/new">
            <button className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg shadow-lg transition">
              + New Request
            </button>
          </Link>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500">
            <p className="text-gray-500 text-sm">Total Requests</p>
            <p className="text-3xl font-bold text-blue-600">{stats.total}</p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-green-500">
            <p className="text-gray-500 text-sm">Active</p>
            <p className="text-3xl font-bold text-green-600">{stats.active}</p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-yellow-500">
            <p className="text-gray-500 text-sm">Suspended</p>
            <p className="text-3xl font-bold text-yellow-600">{stats.suspended}</p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-indigo-500">
            <p className="text-gray-500 text-sm">Fulfilled</p>
            <p className="text-3xl font-bold text-indigo-600">{stats.fulfilled}</p>
          </div>
        </div>

        {/* Filter Tabs */}
        <div className="flex gap-2 mb-6 bg-white rounded-lg p-2 shadow-md">
          {['ACTIVE', 'SUSPENDED', 'FULFILLED', 'CANCELLED'].map((status) => (
            <button
              key={status}
              onClick={() => setFilterStatus(status)}
              className={`px-4 py-2 rounded font-semibold transition ${
                filterStatus === status
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {status}
            </button>
          ))}
        </div>

        {/* Requests List */}
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          {loading && (
            <div className="p-8 text-center">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              <p className="text-gray-600 mt-4">Loading requests...</p>
            </div>
          )}

          {error && (
            <div className="p-6 bg-red-50 border-l-4 border-red-500">
              <p className="text-red-700 font-semibold">Error</p>
              <p className="text-red-600">{error}</p>
            </div>
          )}

          {!loading && !error && requests.length === 0 && (
            <div className="p-12 text-center">
              <p className="text-gray-500 text-lg mb-4">No requests found</p>
              <Link href="/pin/request/new">
                <button className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
                  Create First Request
                </button>
              </Link>
            </div>
          )}

          {!loading && requests.length > 0 && (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Title</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Category</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Priority</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Status</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Created</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {requests.map((req) => (
                    <tr key={req.id} className="hover:bg-gray-50 transition">
                      <td className="px-6 py-4">
                        <Link href={`/pin/request/${req.id}`}>
                          <span className="text-blue-600 hover:text-blue-800 font-semibold cursor-pointer">
                            {req.title}
                          </span>
                        </Link>
                      </td>
                      <td className="px-6 py-4 text-gray-700">{req.category}</td>
                      <td className="px-6 py-4">
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getPriorityBadge(req.priority)}`}>
                          {req.priority}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusBadge(req.status)}`}>
                          {req.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-gray-600 text-sm">
                        {new Date(req.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4">
                        <Link href={`/pin/request/${req.id}`}>
                          <button className="text-blue-600 hover:text-blue-800 font-semibold">View</button>
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
