'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import Link from 'next/link';
import Header from '../../components/Header';
import RequestCard from '../../components/RequestCard';
import RequestCardGrid from '../../components/RequestCardGrid';

export default function PINDashboard() {
  const [requests, setRequests] = useState([]);
  const [filteredRequests, setFilteredRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterStatus, setFilterStatus] = useState('ACTIVE');
  const [searchKeyword, setSearchKeyword] = useState('');
  const [searchServiceType, setSearchServiceType] = useState('');
  const [serviceTypes, setServiceTypes] = useState([]);

  useEffect(() => {
    fetchRequests();
    fetchServiceTypes();
  }, [filterStatus]);

  useEffect(() => {
    applyFilters();
  }, [requests, searchKeyword, searchServiceType]);

  const fetchServiceTypes = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const response = await axios.get(
        'http://localhost:5000/api/requests/service-types',
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (response.data.success) {
        setServiceTypes(response.data.data || []);
      }
    } catch (err) {
      console.error('Error fetching service types:', err);
    }
  };

  const applyFilters = () => {
    let filtered = [...requests];

    // Filter by keyword (search in title and description)
    if (searchKeyword.trim()) {
      const keyword = searchKeyword.toLowerCase();
      filtered = filtered.filter(req => 
        req.title?.toLowerCase().includes(keyword) ||
        req.description?.toLowerCase().includes(keyword)
      );
    }

    // Filter by service type
    if (searchServiceType) {
      filtered = filtered.filter(req => req.service_type === searchServiceType);
    }

    setFilteredRequests(filtered);
  };

  const clearFilters = () => {
    setSearchKeyword('');
    setSearchServiceType('');
  };

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

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Header title="PIN Dashboard - Manage Requests" subtitle="Manage your service requests" />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Action Button */}
        <div className="flex justify-end mb-6">
          <Link href="/pin/request/new">
            <button className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg shadow-lg transition">
              + New Request
            </button>
          </Link>
        </div>

        {/* Filter Tabs */}
        <div className="flex gap-2 mb-6 bg-white rounded-lg p-2 shadow-md">
          {['ACTIVE', 'SUSPENDED', 'FULFILLED'].map((status) => (
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

        {/* Search and Filter Section */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-gray-800">Search & Filter</h3>
            {(searchKeyword || searchServiceType) && (
              <button
                onClick={clearFilters}
                className="text-sm text-blue-600 hover:text-blue-800 font-semibold"
              >
                Clear Filters
              </button>
            )}
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Keyword Search */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Search by Keyword
              </label>
              <div className="relative">
                <input
                  type="text"
                  value={searchKeyword}
                  onChange={(e) => setSearchKeyword(e.target.value)}
                  placeholder="Search in title or description..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
                />
                <svg
                  className="absolute left-3 top-2.5 h-5 w-5 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
              </div>
            </div>

            {/* Service Type Filter */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Filter by Service Type
              </label>
              <select
                value={searchServiceType}
                onChange={(e) => setSearchServiceType(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
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

          {/* Results Count */}
          {(searchKeyword || searchServiceType) && (
            <div className="mt-4 text-sm text-gray-600">
              Found <span className="font-bold text-blue-600">{filteredRequests.length}</span> result(s)
            </div>
          )}
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
            <div className="p-6">
              <RequestCardGrid
                emptyMessage="No requests match your search criteria"
                emptyIcon="🔍"
                emptyAction={
                  <button 
                    onClick={clearFilters}
                    className="mt-4 bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                  >
                    Clear Filters
                  </button>
                }
              >
                {filteredRequests.map((req) => (
                  <RequestCard
                    key={req.id}
                    request={req}
                    onClick={() => window.location.href = `/pin/request/${req.id}`}
                    theme="blue"
                  />
                ))}
              </RequestCardGrid>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
