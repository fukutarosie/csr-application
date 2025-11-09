'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import Header from '../../../components/Header';
import Alert from '../../../components/Alert';
import { useToast } from '../../../components/ToastProvider';

export default function CompletedMatches() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const toast = useToast();
  
  // Date filters
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [serviceType, setServiceType] = useState('');
  const [serviceTypes, setServiceTypes] = useState([]);
  
  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);

  const getToken = () => localStorage.getItem('token');

  useEffect(() => {
    // Check auth
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');

    if (!token || !userData) {
      router.push('/');
      return;
    }

    const parsedUser = JSON.parse(userData);
    if (parsedUser.role.role_name !== 'PIN') {
      router.push('/');
      return;
    }

    setUser(parsedUser);
    fetchCompletedMatches();
    fetchServiceTypes();
  }, [router]);

  useEffect(() => {
    if (user) {
      fetchCompletedMatches();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentPage, startDate, endDate, serviceType]);

  const fetchCompletedMatches = async () => {
    setLoading(true);
    setError('');
    
    try {
      const params = {
        page: currentPage,
        limit: 10
      };
      
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;
      if (serviceType) params.service_type = serviceType;

      const response = await axios.get('http://localhost:5000/api/requests/history', {
        headers: { 'Authorization': `Bearer ${getToken()}` },
        params
      });

      if (response.data.success) {
        setMatches(response.data.data);
        
        if (response.data.pagination) {
          setTotalPages(response.data.pagination.total_pages);
          setTotalItems(response.data.pagination.total);
        }
      }
    } catch (err) {
      const msg = 'Failed to fetch completed matches';
      setError(msg);
      toast.error(msg);
      console.error(err);
    } finally {
      setLoading(false);
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
      console.error('Failed to load service types', err);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    });
  };

  if (loading && matches.length === 0) {
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
      <Header title="Completed Matches" subtitle="View your fulfilled requests and CSR matches" />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && <Alert type="error" message={error} onClose={() => setError('')} />}

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Start Date</label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => {
                  setCurrentPage(1);
                  setStartDate(e.target.value);
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">End Date</label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => {
                  setCurrentPage(1);
                  setEndDate(e.target.value);
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Service Type</label>
              <select
                value={serviceType}
                onChange={(e) => {
                  setCurrentPage(1);
                  setServiceType(e.target.value);
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
                  setCurrentPage(1);
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Clear Filters
              </button>
            </div>
          </div>
        </div>

        {/* Summary Stats */}
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <p className="text-sm text-gray-600">
            Total completed matches: <span className="font-semibold">{totalItems}</span>
          </p>
        </div>

        {/* Completed Matches List */}
        <div className="space-y-6">
          {matches.length === 0 ? (
            <div className="bg-white rounded-lg shadow text-center py-12">
              <div className="text-6xl mb-4">🎉</div>
              <p className="text-gray-600 mb-2">No completed matches yet</p>
              <p className="text-sm text-gray-500">When your requests are fulfilled, they will appear here</p>
            </div>
          ) : (
            matches.map((match) => (
              <div key={match.id} className="bg-white rounded-lg shadow overflow-hidden">
                <div className="p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex-1">
                      <h3 className="text-lg font-bold text-gray-900 mb-2">{match.title}</h3>
                      <p className="text-sm text-gray-600 mb-2">{match.description}</p>
                      <div className="flex flex-wrap gap-2 mb-3">
                        <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
                          {match.category}
                        </span>
                        {match.service_type && (
                          <span className="px-2 py-1 text-xs font-medium bg-purple-100 text-purple-800 rounded-full">
                            {match.service_type}
                          </span>
                        )}
                        <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">
                          FULFILLED
                        </span>
                      </div>
                    </div>
                    <div className="text-right ml-4">
                      <p className="text-sm text-gray-500">Fulfilled on</p>
                      <p className="text-sm font-semibold text-gray-900">{formatDate(match.fulfilled_at)}</p>
                    </div>
                  </div>

                  {/* Location Info */}
                  {match.location_city && (
                    <div className="mb-4 pb-4 border-b border-gray-200">
                      <p className="text-sm text-gray-600">
                        📍 <span className="font-medium">{match.location_city}</span>
                        {match.location_detail && ` - ${match.location_detail}`}
                      </p>
                    </div>
                  )}

                  {/* CSR Match Details */}
                  {match.matched_csr && match.matched_csr.length > 0 ? (
                    <div className="bg-green-50 border-l-4 border-green-400 p-4 rounded">
                      <h4 className="font-semibold text-green-900 mb-3">Matched CSR Representative</h4>
                      {match.matched_csr.map((csr) => (
                        <div key={csr.id} className="space-y-2">
                          <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                              <p className="text-green-700 font-medium">CSR User ID</p>
                              <p className="text-green-900">#{csr.csr_user_id}</p>
                            </div>
                            {csr.volunteered_hours && (
                              <div>
                                <p className="text-green-700 font-medium">Volunteer Rating</p>
                                <p className="text-green-900">⭐ {csr.volunteered_hours}/5</p>
                              </div>
                            )}
                          </div>
                          
                          {csr.completion_date && (
                            <div className="text-sm">
                              <p className="text-green-700 font-medium">Completion Date</p>
                              <p className="text-green-900">{formatDate(csr.completion_date)}</p>
                            </div>
                          )}

                          {csr.notes && (
                            <div className="text-sm">
                              <p className="text-green-700 font-medium">CSR Notes</p>
                              <p className="text-green-900 italic">"{csr.notes}"</p>
                            </div>
                          )}

                          {csr.feedback_from_pin && (
                            <div className="text-sm">
                              <p className="text-green-700 font-medium">Your Feedback</p>
                              <p className="text-green-900 italic">"{csr.feedback_from_pin}"</p>
                            </div>
                          )}

                          {!csr.feedback_from_pin && (
                            <div className="mt-2">
                              <button
                                onClick={() => router.push(`/pin/request/${match.id}?action=feedback`)}
                                className="text-sm text-blue-600 hover:text-blue-800 font-medium"
                              >
                                + Add Feedback for CSR
                              </button>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="bg-gray-50 border-l-4 border-gray-400 p-4 rounded">
                      <p className="text-gray-600 text-sm">
                        This request was marked as fulfilled but no CSR match details are available.
                      </p>
                    </div>
                  )}

                  {/* Request Details */}
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <p className="text-gray-500">Created</p>
                        <p className="font-medium">{formatDate(match.created_at)}</p>
                      </div>
                      <div>
                        <p className="text-gray-500">Priority</p>
                        <p className="font-medium">{match.priority}</p>
                      </div>
                      <div>
                        <p className="text-gray-500">Views</p>
                        <p className="font-medium">👁️ {match.view_count || 0}</p>
                      </div>
                      <div>
                        <p className="text-gray-500">Shortlists</p>
                        <p className="font-medium">⭐ {match.shortlist_count || 0}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="mt-6 flex justify-center">
            <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
              <button
                onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                disabled={currentPage === 1}
                className="relative inline-flex items-center px-4 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <span className="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700">
                Page {currentPage} of {totalPages}
              </span>
              <button
                onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                disabled={currentPage === totalPages}
                className="relative inline-flex items-center px-4 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </nav>
          </div>
        )}
      </main>
    </div>
  );
}
