'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import Header from '../../components/Header';
import Alert from '../../components/Alert';

export default function MyShortlist() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [shortlist, setShortlist] = useState([]);
  const [serviceTypes, setServiceTypes] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [searchServiceType, setSearchServiceType] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [editingItem, setEditingItem] = useState(null);
  const [editForm, setEditForm] = useState({ status: '', notes: '', volunteered_hours: '' });

  const getToken = () => localStorage.getItem('token');

  useEffect(() => {
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
    fetchShortlist();
    fetchServiceTypes();
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

  const fetchShortlist = async () => {
    try {
      const params = statusFilter ? { status: statusFilter } : {};
      const response = await axios.get('http://localhost:5000/api/shortlist', {
        headers: { 'Authorization': `Bearer ${getToken()}` },
        params
      });

      if (response.data.success) {
        setShortlist(response.data.data);
      }
    } catch (err) {
      console.error('Failed to fetch shortlist:', err);
      setError('Failed to load shortlist');
    }
  };

  const handleRemove = async (shortlistId) => {
    if (!confirm('Are you sure you want to remove this request from your shortlist?')) return;

    try {
      const response = await axios.delete(
        `http://localhost:5000/api/shortlist/${shortlistId}`,
        { headers: { 'Authorization': `Bearer ${getToken()}` } }
      );

      if (response.data.success) {
        setSuccess('Removed from shortlist successfully');
        fetchShortlist();
      }
    } catch (err) {
      console.error('Failed to remove:', err);
      setError('Failed to remove from shortlist');
    }
  };

  const handleEditClick = (item) => {
    setEditingItem(item.id);
    setEditForm({
      status: item.status,
      notes: item.notes || '',
      volunteered_hours: item.volunteered_hours || ''
    });
  };

  const handleUpdateStatus = async (shortlistId) => {
    try {
      const payload = {
        status: editForm.status,
        notes: editForm.notes || undefined,
        volunteered_hours: editForm.volunteered_hours ? parseFloat(editForm.volunteered_hours) : undefined
      };

      const response = await axios.patch(
        `http://localhost:5000/api/shortlist/${shortlistId}/status`,
        payload,
        { headers: { 'Authorization': `Bearer ${getToken()}` } }
      );

      if (response.data.success) {
        setSuccess('Status updated successfully');
        setEditingItem(null);
        fetchShortlist();
      }
    } catch (err) {
      console.error('Failed to update status:', err);
      setError('Failed to update status');
    }
  };

  const handleFilterChange = (status) => {
    setStatusFilter(status);
  };

  const filteredShortlist = shortlist.filter(item => {
    const matchesServiceType = !searchServiceType || 
      item.requests?.service_type === searchServiceType;
    
    const matchesDateRange = (() => {
      if (!startDate && !endDate) return true;
      const requestDate = new Date(item.requests?.requested_by_date);
      if (startDate && new Date(startDate) > requestDate) return false;
      if (endDate && new Date(endDate) < requestDate) return false;
      return true;
    })();
    
    return matchesServiceType && matchesDateRange;
  });

  const clearFilters = () => {
    setSearchServiceType('');
    setStartDate('');
    setEndDate('');
  };

  useEffect(() => {
    if (user) {
      fetchShortlist();
    }
  }, [statusFilter]);

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
      <Header title="My Shortlist" subtitle="Manage your shortlisted requests" />

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

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filter Tabs */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="flex border-b">
            <button
              onClick={() => handleFilterChange('')}
              className={`flex-1 px-6 py-3 text-sm font-medium ${!statusFilter ? 'border-b-2 border-purple-600 text-purple-600' : 'text-gray-500 hover:text-gray-700'}`}
            >
              All ({shortlist.length})
            </button>
            <button
              onClick={() => handleFilterChange('SHORTLISTED')}
              className={`flex-1 px-6 py-3 text-sm font-medium ${statusFilter === 'SHORTLISTED' ? 'border-b-2 border-purple-600 text-purple-600' : 'text-gray-500 hover:text-gray-700'}`}
            >
              Shortlisted
            </button>
            <button
              onClick={() => handleFilterChange('IN_PROGRESS')}
              className={`flex-1 px-6 py-3 text-sm font-medium ${statusFilter === 'IN_PROGRESS' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
            >
              In Progress
            </button>
            <button
              onClick={() => handleFilterChange('COMPLETED')}
              className={`flex-1 px-6 py-3 text-sm font-medium ${statusFilter === 'COMPLETED' ? 'border-b-2 border-green-600 text-green-600' : 'text-gray-500 hover:text-gray-700'}`}
            >
              Completed
            </button>
            <button
              onClick={() => handleFilterChange('DECLINED')}
              className={`flex-1 px-6 py-3 text-sm font-medium ${statusFilter === 'DECLINED' ? 'border-b-2 border-red-600 text-red-600' : 'text-gray-500 hover:text-gray-700'}`}
            >
              Declined
            </button>
          </div>
        </div>

        {/* Search Filters */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">🔍 Filter Shortlist</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Service Type</label>
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
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">From Date</label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">To Date</label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>
          </div>
          {(searchServiceType || startDate || endDate) && (
            <div className="mt-3 flex items-center justify-between">
              <p className="text-sm text-gray-600">
                Found {filteredShortlist.length} {filteredShortlist.length === 1 ? 'item' : 'items'}
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

        {/* Shortlist Items */}
        {filteredShortlist.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <div className="text-6xl mb-4">📋</div>
            <h3 className="text-xl font-semibold mb-2">No Items in Shortlist</h3>
            <p className="text-gray-600 mb-4">Start browsing PIN requests to add to your shortlist</p>
            <button
              onClick={() => router.push('/csr/browse')}
              className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
            >
              Browse Requests
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredShortlist.map((item) => (
              <div key={item.id} className="bg-white rounded-lg shadow p-6">
                {editingItem === item.id ? (
                  // Edit Mode
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold">{item.requests?.title}</h3>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
                        <select
                          value={editForm.status}
                          onChange={(e) => setEditForm({ ...editForm, status: e.target.value })}
                          className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                        >
                          <option value="SHORTLISTED">Shortlisted</option>
                          <option value="IN_PROGRESS">In Progress</option>
                          <option value="COMPLETED">Completed</option>
                          <option value="DECLINED">Declined</option>
                        </select>
                      </div>

                      {editForm.status === 'COMPLETED' && (
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">Hours Volunteered</label>
                          <input
                            type="number"
                            step="0.5"
                            value={editForm.volunteered_hours}
                            onChange={(e) => setEditForm({ ...editForm, volunteered_hours: e.target.value })}
                            className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                            placeholder="0.0"
                          />
                        </div>
                      )}

                      <div className="md:col-span-2">
                        <label className="block text-sm font-medium text-gray-700 mb-2">Notes</label>
                        <textarea
                          value={editForm.notes}
                          onChange={(e) => setEditForm({ ...editForm, notes: e.target.value })}
                          className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                          rows="2"
                          placeholder="Add notes about your volunteering..."
                        />
                      </div>
                    </div>

                    <div className="flex gap-2">
                      <button
                        onClick={() => handleUpdateStatus(item.id)}
                        className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                      >
                        Save Changes
                      </button>
                      <button
                        onClick={() => setEditingItem(null)}
                        className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  // View Mode
                  <div>
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">{item.requests?.title}</h3>
                        <p className="text-sm text-gray-600 mb-3">{item.requests?.description}</p>
                        
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <span className="font-medium text-gray-700">Category:</span>
                            <p className="text-gray-600">{item.requests?.category}</p>
                          </div>
                          <div>
                            <span className="font-medium text-gray-700">Service Type:</span>
                            <p className="text-gray-600">{item.requests?.service_type}</p>
                          </div>
                          <div>
                            <span className="font-medium text-gray-700">Priority:</span>
                            <p className="text-gray-600">{item.requests?.priority}</p>
                          </div>
                          <div>
                            <span className="font-medium text-gray-700">Location:</span>
                            <p className="text-gray-600">{item.requests?.location_city}</p>
                          </div>
                        </div>

                        {item.notes && (
                          <div className="mt-3 p-3 bg-gray-50 rounded">
                            <p className="text-sm text-gray-700"><strong>Notes:</strong> {item.notes}</p>
                          </div>
                        )}

                        {item.volunteered_hours && (
                          <div className="mt-2">
                            <span className="text-sm font-medium text-green-600">
                              ⏰ {item.volunteered_hours} hours volunteered
                            </span>
                          </div>
                        )}
                      </div>
                      
                      <div className="ml-4">
                        <StatusBadge status={item.status} />
                        <p className="text-xs text-gray-500 mt-2">
                          Added: {new Date(item.shortlisted_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>

                    <div className="flex gap-2 pt-4 border-t">
                      <button
                        onClick={() => handleEditClick(item)}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                      >
                        ✏️ Update Status
                      </button>
                      <button
                        onClick={() => handleRemove(item.id)}
                        className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                      >
                        🗑️ Remove
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
