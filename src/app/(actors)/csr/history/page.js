'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import Header from '../../../components/Header';
import Alert from '../../../components/Alert';
import { useToast } from '../../../components/ToastProvider';

export default function CSRHistory() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [completedItems, setCompletedItems] = useState([]);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState('');
  const toast = useToast();
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [serviceType, setServiceType] = useState('');
  const [serviceTypes, setServiceTypes] = useState([]);

  const getToken = () => localStorage.getItem('token');

  useEffect(() => {
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');

    if (!token || !userData) {
      router.push('/');
      return;
    }

    const parsedUser = JSON.parse(userData);
    if (parsedUser.role.role_name !== 'CSR Rep') {
      router.push('/');
      return;
    }

    setUser(parsedUser);
    fetchHistory();
    fetchStats();
    fetchServiceTypes();
    setLoading(false);
  }, [router]);

  useEffect(() => {
    if (user) {
      fetchHistory();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [startDate, endDate, serviceType]);

  const fetchHistory = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/shortlist', {
        headers: { 'Authorization': `Bearer ${getToken()}` },
        params: {
          status: 'COMPLETED',
          start_date: startDate || undefined,
          end_date: endDate || undefined,
          service_type: serviceType || undefined
        }
      });

      if (response.data.success) {
        setCompletedItems(response.data.data);
      }
    } catch (err) {
      console.error('Failed to fetch history:', err);
      const msg = 'Failed to load history';
      setError(msg);
      toast.error(msg);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/shortlist/stats', {
        headers: { 'Authorization': `Bearer ${getToken()}` }
      });

      if (response.data.success) {
        setStats(response.data.data);
      }
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  };

  const fetchServiceTypes = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/requests/service-types');
      const actualData = Array.isArray(response.data) ? response.data[0] : response.data;
      if (actualData?.success) {
        setServiceTypes(actualData.data || []);
      }
    } catch (err) {
      console.error('Failed to fetch service types:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-100">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <Header title="Volunteering History" subtitle="Your completed volunteering activities" />

      {error && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <Alert type="error" message={error} onClose={() => setError('')} />
        </div>
      )}

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4 text-gray-900">Filter Completed Activities</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Start Date</label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">End Date</label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Service Type</label>
              <select
                value={serviceType}
                onChange={(e) => setServiceType(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                <option value="">All Service Types</option>
                {serviceTypes.map((type) => (
                  <option key={type.id} value={type.service_name}>
                    {type.service_name}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex items-end">
              <button
                onClick={() => {
                  setStartDate('');
                  setEndDate('');
                  setServiceType('');
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Clear Filters
              </button>
            </div>
          </div>
        </div>

        {/* Statistics Summary */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg shadow p-6 text-white">
              <div className="text-sm opacity-90 mb-1">Total Completed</div>
              <div className="text-4xl font-bold">{stats.completed}</div>
            </div>
            
            <div className="bg-gradient-to-br from-yellow-500 to-yellow-600 rounded-lg shadow p-6 text-white">
              <div className="text-sm opacity-90 mb-1">Total Rating Points</div>
              <div className="text-4xl font-bold">{stats.totalHoursVolunteered || 0}</div>
            </div>

            <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg shadow p-6 text-white">
              <div className="text-sm opacity-90 mb-1">Total Shortlisted</div>
              <div className="text-4xl font-bold">{stats.totalShortlisted}</div>
            </div>

            <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg shadow p-6 text-white">
              <div className="text-sm opacity-90 mb-1">In Progress</div>
              <div className="text-4xl font-bold">{stats.inProgress}</div>
            </div>
          </div>
        )}

        {/* Completed Activities */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Completed Volunteering Activities</h2>
          </div>

          {completedItems.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <div className="text-6xl mb-4">🎉</div>
              <h3 className="text-xl font-semibold mb-2">No Completed Activities Yet</h3>
              <p className="text-gray-600 mb-4">Start volunteering by browsing available requests</p>
              <button
                onClick={() => router.push('/csr/browse')}
                className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
              >
                Browse Requests
              </button>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {completedItems.map((item) => (
                <div key={item.id} className="p-6 hover:bg-gray-50">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">
                        {item.requests?.title}
                      </h3>
                      <p className="text-sm text-gray-600 mb-3">{item.requests?.description}</p>
                      
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-3">
                        <div>
                          <span className="font-medium text-gray-700">Category:</span>
                          <p className="text-gray-600">{item.requests?.category}</p>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Service Type:</span>
                          <p className="text-gray-600">{item.requests?.service_type}</p>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Location:</span>
                          <p className="text-gray-600">{item.requests?.location_city}, {item.requests?.location_state}</p>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Priority:</span>
                          <p className="text-gray-600">{item.requests?.priority}</p>
                        </div>
                      </div>

                      <div className="flex flex-wrap gap-4 text-sm">
                        <div className="flex items-center">
                          <span className="text-green-600 font-semibold mr-2">⭐</span>
                          <span className="text-gray-700">
                            <strong>Volunteer Rating:</strong> {item.volunteered_hours ? `${item.volunteered_hours}/5` : 'Not rated yet'}
                          </span>
                        </div>
                        <div className="flex items-center">
                          <span className="text-blue-600 font-semibold mr-2">📅</span>
                          <span className="text-gray-700">
                            <strong>Completed:</strong> {new Date(item.updated_at).toLocaleDateString()}
                          </span>
                        </div>
                        <div className="flex items-center">
                          <span className="text-purple-600 font-semibold mr-2">📆</span>
                          <span className="text-gray-700">
                            <strong>Shortlisted:</strong> {new Date(item.shortlisted_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>

                      {item.notes && (
                        <div className="mt-3 p-3 bg-blue-50 rounded">
                          <p className="text-sm text-gray-700">
                            <strong>Your Notes:</strong> {item.notes}
                          </p>
                        </div>
                      )}

                      {item.feedback_from_pin && (
                        <div className="mt-3 p-3 bg-green-50 rounded">
                          <p className="text-sm text-gray-700">
                            <strong>Feedback from PIN:</strong> {item.feedback_from_pin}
                          </p>
                        </div>
                      )}
                    </div>

                    <div className="ml-4">
                      <span className="px-3 py-1 bg-green-100 text-green-800 text-sm font-medium rounded-full">
                        ✅ Completed
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Back to Dashboard */}
        <div className="mt-8 text-center">
          <button
            onClick={() => router.push('/csr')}
            className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
          >
            ← Back to Dashboard
          </button>
        </div>
      </main>
    </div>
  );
}
