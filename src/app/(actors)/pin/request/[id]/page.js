'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useParams } from 'next/navigation';
import Header from '../../../../components/Header';

export default function RequestDetail() {
  const router = useRouter();
  const params = useParams();
  const requestId = params.id;

  const [request, setRequest] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [formData, setFormData] = useState({});
  const [updating, setUpdating] = useState(false);
  const [suspending, setSuspending] = useState(false);
  const [suspendReason, setSuspendReason] = useState('');

  const [serviceTypes, setServiceTypes] = useState([]);

  useEffect(() => {
    fetchRequest();
    fetchLookupData();
  }, [requestId]);

  const fetchRequest = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      if (!token) {
        setError('Not authenticated');
        return;
      }

      const response = await axios.get(
        `http://localhost:5000/api/requests/${requestId}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.data.success) {
        setRequest(response.data.data);
        setFormData(response.data.data);
      } else {
        setError(response.data.message);
      }
    } catch (err) {
      setError(err.response?.data?.message || err.message);
      console.error('Error fetching request:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchLookupData = async () => {
    try {
      const typesRes = await axios.get(
        'http://localhost:5000/api/requests/service-types'
      );
      
      // Handle if response.data is an array (double-wrapped)
      const actualData = Array.isArray(typesRes.data) ? typesRes.data[0] : typesRes.data;
      
      if (actualData && actualData.success) {
        setServiceTypes(actualData.data || []);
      }
    } catch (err) {
      console.error('Error fetching lookup data:', err);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    setUpdating(true);
    setError(null);
    setSuccess(null);

    try {
      const token = localStorage.getItem('token');
      
      const updates = {};
      ['title', 'description', 'service_type', 'region', 'requested_by_date', 'image_url'].forEach(key => {
        if (formData[key] !== request[key]) {
          updates[key] = formData[key];
        }
      });

      if (Object.keys(updates).length === 0) {
        setEditMode(false);
        setUpdating(false);
        return;
      }

      const response = await axios.put(
        `http://localhost:5000/api/requests/${requestId}`,
        updates,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.data.success) {
        setRequest(response.data.data);
        setFormData(response.data.data);
        setEditMode(false);
        setSuccess('Request updated successfully!');
        
        // Clear success message after 3 seconds
        setTimeout(() => setSuccess(null), 3000);
      } else {
        setError(response.data.message);
      }
    } catch (err) {
      setError(err.response?.data?.message || err.message);
      console.error('Error updating request:', err);
    } finally {
      setUpdating(false);
    }
  };

  const handleSuspend = async (e) => {
    e.preventDefault();
    setSuspending(true);
    setError(null);
    setSuccess(null);

    try {
      const token = localStorage.getItem('token');
      
      const response = await axios.put(
        `http://localhost:5000/api/requests/${requestId}/suspend`,
        { reason: suspendReason || null },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.data.success) {
        setRequest(response.data.data);
        setSuspendReason('');
        setEditMode(false);
        setSuccess('Request suspended successfully!');
        
        // Clear success message after 3 seconds
        setTimeout(() => setSuccess(null), 3000);
      } else {
        setError(response.data.message);
      }
    } catch (err) {
      setError(err.response?.data?.message || err.message);
      console.error('Error suspending request:', err);
    } finally {
      setSuspending(false);
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

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100">
        <Header title="Request Details" />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex items-center justify-center">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="text-gray-600 mt-4">Loading request...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error && !request) {
    return (
      <div className="min-h-screen bg-gray-100">
        <Header title="Request Details" />
        <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Link href="/pin/dashboard">
            <button className="text-blue-600 hover:text-blue-800 font-semibold mb-4">
              ← Back to Dashboard
            </button>
          </Link>
          <div className="bg-red-50 border-l-4 border-red-500 rounded p-6">
            <p className="text-red-700 font-semibold">Error</p>
            <p className="text-red-600">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!request) {
    return (
      <div className="min-h-screen bg-gray-100">
        <Header title="Request Details" />
        <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <p className="text-gray-700">Request not found</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <Header title="Request Details" subtitle={request.title} />
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Back Button */}
        <Link href="/pin/dashboard">
          <button className="text-blue-600 hover:text-blue-800 font-semibold mb-6">
            ← Back to Dashboard
          </button>
        </Link>
        
        {/* Request Header */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex justify-between items-start">
            <div>
              <h2 className="text-2xl font-bold text-gray-800 mb-3">{request.title}</h2>
              <div className="flex gap-3">
                <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getStatusBadge(request.status)}`}>
                  {request.status}
                </span>
                <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getPriorityBadge(request.priority)}`}>
                  {request.priority}
                </span>
              </div>
            </div>
            {request.status === 'ACTIVE' && !editMode && (
              <button
                onClick={() => setEditMode(true)}
                className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
              >
                Edit
              </button>
            )}
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-500 rounded">
            <p className="text-red-700 font-semibold">Error</p>
            <p className="text-red-600">{error}</p>
          </div>
        )}

        {/* Success Message */}
        {success && (
          <div className="mb-6 p-4 bg-green-50 border-l-4 border-green-500 rounded">
            <p className="text-green-700 font-semibold">Success</p>
            <p className="text-green-600">{success}</p>
          </div>
        )}

        {!editMode ? (
          <>
            {/* View Mode */}
            <div className="bg-white rounded-lg shadow-lg p-8 mb-6">
              {/* Image Display */}
              {request.image_url && (
                <div className="mb-8">
                  <p className="text-gray-500 text-sm font-semibold uppercase mb-3">Request Image</p>
                  <img 
                    src={`http://localhost:5000${request.image_url}`}
                    alt={request.title}
                    className="w-full max-h-96 object-cover rounded-lg border-2 border-gray-200 shadow-sm"
                  />
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Left Column */}
                <div>
                  <div className="mb-6">
                    <p className="text-gray-500 text-sm font-semibold uppercase">Service Type</p>
                    <p className="text-gray-800 text-lg">{request.service_type || 'Not specified'}</p>
                  </div>
                  <div className="mb-6">
                    <p className="text-gray-500 text-sm font-semibold uppercase">Region</p>
                    <p className="text-gray-800 text-lg">{request.region || 'Not specified'}</p>
                  </div>
                  <div className="mb-6">
                    <p className="text-gray-500 text-sm font-semibold uppercase">Created</p>
                    <p className="text-gray-800 text-lg">
                      {new Date(request.created_at).toLocaleDateString()} {new Date(request.created_at).toLocaleTimeString()}
                    </p>
                  </div>
                </div>

                {/* Right Column */}
                <div>
                  <div className="mb-6">
                    <p className="text-gray-500 text-sm font-semibold uppercase">Requested By</p>
                    <p className="text-gray-800 text-lg">
                      {request.requested_by_date ? new Date(request.requested_by_date).toLocaleDateString() : 'Not specified'}
                    </p>
                  </div>
                  <div className="mb-6">
                    <p className="text-gray-500 text-sm font-semibold uppercase">Last Updated</p>
                    <p className="text-gray-800 text-lg">
                      {new Date(request.updated_at).toLocaleDateString()} {new Date(request.updated_at).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              </div>

              {/* Description */}
              <div className="mt-8 pt-8 border-t border-gray-200">
                <p className="text-gray-500 text-sm font-semibold uppercase mb-3">Description</p>
                <p className="text-gray-800 text-base leading-relaxed whitespace-pre-wrap">
                  {request.description}
                </p>
              </div>
            </div>

            {/* Action Buttons */}
            {request.status === 'ACTIVE' && (
              <div className="bg-white rounded-lg shadow-lg p-6">
                <form onSubmit={handleSuspend}>
                  <div className="mb-4">
                    <label className="block text-gray-700 font-semibold mb-2">
                      Suspend Request
                    </label>
                    <textarea
                      value={suspendReason}
                      onChange={(e) => setSuspendReason(e.target.value)}
                      placeholder="Optional: Reason for suspension"
                      rows="3"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-600"
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={suspending}
                    className="w-full bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-400 text-white font-bold py-3 rounded-lg transition"
                  >
                    {suspending ? 'Suspending...' : 'Suspend This Request'}
                  </button>
                </form>
              </div>
            )}
          </>
        ) : (
          <>
            {/* Edit Mode */}
            <form onSubmit={handleUpdate} className="bg-white rounded-lg shadow-lg p-8">
              <div className="mb-6">
                <label className="block text-gray-700 font-semibold mb-2">Title</label>
                <input
                  type="text"
                  name="title"
                  value={formData.title || ''}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
                />
              </div>

              <div className="mb-6">
                <label className="block text-gray-700 font-semibold mb-2">Description</label>
                <textarea
                  name="description"
                  value={formData.description || ''}
                  onChange={handleChange}
                  rows="5"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div>
                  <label className="block text-gray-700 font-semibold mb-2">Service Type *</label>
                  <select
                    name="service_type"
                    value={formData.service_type || ''}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
                    required
                  >
                    <option value="">Select service type</option>
                    {serviceTypes.map(type => (
                      <option key={type.id} value={type.service_name}>{type.service_name}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div>
                  <label className="block text-gray-700 font-semibold mb-2">Region *</label>
                  <input
                    type="text"
                    name="region"
                    value={formData.region || ''}
                    onChange={handleChange}
                    placeholder="e.g. Hougang, Sengkang, Bugis, Clementi"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
                    required
                  />
                </div>

                <div>
                  <label className="block text-gray-700 font-semibold mb-2">Requested By Date *</label>
                  <input
                    type="date"
                    name="requested_by_date"
                    value={formData.requested_by_date || ''}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
                    required
                  />
                </div>
              </div>

              <div className="flex gap-4">
                <button
                  type="submit"
                  disabled={updating}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-bold py-3 rounded-lg transition"
                >
                  {updating ? 'Updating...' : 'Save Changes'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setEditMode(false);
                    setFormData(request);
                    setError(null);
                  }}
                  className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-3 rounded-lg transition"
                >
                  Cancel
                </button>
              </div>
            </form>
          </>
        )}
      </div>
    </div>
  );
}
