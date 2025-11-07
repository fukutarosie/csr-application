'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import Header from '../components/Header';
import Alert from '../components/Alert';
import RequestCard from '../components/RequestCard';
import RequestCardGrid from '../components/RequestCardGrid';

export default function CSRDashboard() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [requests, setRequests] = useState([]);
  const [serviceTypes, setServiceTypes] = useState([]);
  const [shortlistedIds, setShortlistedIds] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [searchKeyword, setSearchKeyword] = useState('');
  const [searchServiceType, setSearchServiceType] = useState('');
  const [addingToShortlist, setAddingToShortlist] = useState(null);

  const getToken = () => localStorage.getItem('token');

  useEffect(() => {
    // Check if user is logged in and has CSR Rep role
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');

    if (!token || !userData) {
      router.push('/');
      return;
    }

    const parsedUser = JSON.parse(userData);
    if (parsedUser.role.name !== 'CSR Rep') {
      router.push('/');
      return;
    }

    setUser(parsedUser);
    fetchRequests();
    fetchServiceTypes();
    fetchShortlistedIds();
    setLoading(false);
  }, [router]);

  const fetchServiceTypes = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/requests/service-types');
      if (response.data.success) {
        setServiceTypes(response.data.data);
      }
    } catch (err) {
      console.error('Failed to fetch service types:', err);
    }
  };

  const fetchShortlistedIds = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/shortlist', {
        headers: { 'Authorization': `Bearer ${getToken()}` }
      });
      if (response.data.success) {
        const ids = response.data.data.map(item => item.request_id);
        setShortlistedIds(ids);
      }
    } catch (err) {
      console.error('Failed to fetch shortlisted IDs:', err);
    }
  };

  const fetchRequests = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/requests?status=ACTIVE', {
        headers: { 'Authorization': `Bearer ${getToken()}` }
      });
      if (response.data.success) {
        setRequests(response.data.data);
      } else {
        setError(response.data.message);
      }
    } catch (err) {
      console.error('Failed to fetch requests:', err);
      setError('Failed to load opportunities');
    }
  };

  const handleToggleShortlist = async (requestId) => {
    const isCurrentlyShortlisted = shortlistedIds.includes(requestId);
    setAddingToShortlist(requestId);

    try {
      if (isCurrentlyShortlisted) {
        // Remove from shortlist
        await axios.delete(`http://localhost:5000/api/shortlist/${requestId}`, {
          headers: { 'Authorization': `Bearer ${getToken()}` }
        });
        setShortlistedIds(shortlistedIds.filter(id => id !== requestId));
        setSuccess('Removed from shortlist');
      } else {
        // Add to shortlist
        await axios.post('http://localhost:5000/api/shortlist', 
          { request_id: requestId },
          { headers: { 'Authorization': `Bearer ${getToken()}` } }
        );
        setShortlistedIds([...shortlistedIds, requestId]);
        setSuccess('Added to shortlist');
      }
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to update shortlist');
      setTimeout(() => setError(''), 3000);
    } finally {
      setAddingToShortlist(null);
    }
  };

  const clearFilters = () => {
    setSearchKeyword('');
    setSearchServiceType('');
  };

  const filteredRequests = requests.filter(request => {
    const matchesKeyword = !searchKeyword || 
      request.title?.toLowerCase().includes(searchKeyword.toLowerCase()) ||
      request.description?.toLowerCase().includes(searchKeyword.toLowerCase());
    
    const matchesServiceType = !searchServiceType || 
      request.service_type === searchServiceType;
    
    return matchesKeyword && matchesServiceType;
  });

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

  const StatusBadge = ({ status }) => {
    const colors = {
      'SHORTLISTED': 'bg-purple-100 text-purple-800',
      'IN_PROGRESS': 'bg-blue-100 text-blue-800',
      'COMPLETED': 'bg-green-100 text-green-800',
      'DECLINED': 'bg-red-100 text-red-800'
    };
    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${colors[status] || 'bg-gray-100 text-gray-800'}`}>
        {status.replace('_', ' ')}
      </span>
    );
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Header title="CSR Rep Dashboard" subtitle="Find volunteering opportunities" />

      {error && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <Alert type="error" message={error} onClose={() => setError('')} />
        </div>
      )}

      {success && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <Alert type="success" message={success} onClose={() => setSuccess('')} />
        </div>
      )}

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <button
            onClick={() => router.push('/csr/shortlist')}
            className="bg-gradient-to-r from-purple-600 to-purple-700 text-white rounded-lg shadow-lg p-6 hover:from-purple-700 hover:to-purple-800 transition-all transform hover:scale-105"
          >
            <div className="text-4xl mb-3">�</div>
            <h3 className="font-bold text-lg mb-2">My Shortlist</h3>
            <p className="text-sm opacity-90">Manage your shortlisted requests</p>
          </button>

          <button
            onClick={() => router.push('/csr/history')}
            className="bg-gradient-to-r from-green-600 to-green-700 text-white rounded-lg shadow-lg p-6 hover:from-green-700 hover:to-green-800 transition-all transform hover:scale-105"
          >
            <div className="text-4xl mb-3">�</div>
            <h3 className="font-bold text-lg mb-2">History</h3>
            <p className="text-sm opacity-90">View completed volunteering activities</p>
          </button>
        </div>

        {/* Search Panel */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">🔍 Search Opportunities</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="md:col-span-2">
              <input
                type="text"
                placeholder="Search by title or description..."
                value={searchKeyword}
                onChange={(e) => setSearchKeyword(e.target.value)}
                className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>
            <div>
              <select
                value={searchServiceType}
                onChange={(e) => setSearchServiceType(e.target.value)}
                className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="">All Service Types</option>
                {serviceTypes.map((type) => (
                  <option key={type.id} value={type.service_name}>
                    {type.service_name}
                  </option>
                ))}
              </select>
            </div>
          </div>
          {(searchKeyword || searchServiceType) && (
            <div className="mt-3 flex items-center justify-between">
              <p className="text-sm text-gray-600">
                Found {filteredRequests.length} {filteredRequests.length === 1 ? 'opportunity' : 'opportunities'}
              </p>
              <button
                onClick={clearFilters}
                className="px-4 py-2 text-sm bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
              >
                Clear Filters
              </button>
            </div>
          )}
        </div>

        {/* All Opportunities Grid */}
        <RequestCardGrid
          emptyMessage="No Opportunities Found"
          emptyIcon="�"
          emptyAction={
            (searchKeyword || searchServiceType) ? (
              <button
                onClick={clearFilters}
                className="mt-4 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
              >
                Clear Filters
              </button>
            ) : (
              <p className="text-gray-600 mt-2">Check back later for new opportunities</p>
            )
          }
        >
          {filteredRequests.map((request) => {
            const isShortlisted = shortlistedIds.includes(request.id);
            return (
              <RequestCard
                key={request.id}
                request={request}
                onClick={() => router.push(`/csr/browse/${request.id}`)}
                theme="purple"
                actionButton={
                  <div className="flex items-center justify-between pt-4 border-t">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleToggleShortlist(request.id);
                      }}
                      disabled={addingToShortlist === request.id}
                      className={`text-2xl transition-transform hover:scale-110 ${
                        addingToShortlist === request.id ? 'opacity-50' : ''
                      }`}
                      title={isShortlisted ? 'Remove from shortlist' : 'Add to shortlist'}
                    >
                      {isShortlisted ? '❤️' : '🤍'}
                    </button>
                    <button
                      onClick={() => router.push(`/csr/browse/${request.id}`)}
                      className="flex-1 ml-3 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                    >
                      View Details
                    </button>
                  </div>
                }
              />
            );
          })}
        </RequestCardGrid>
      </main>
    </div>
  );
}
