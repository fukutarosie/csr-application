'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import Header from '../../components/Header';
import { useToast } from '../../components/ToastProvider';
import RequestCard from '../../components/RequestCard';
import RequestCardGrid from '../../components/RequestCardGrid';

export default function PINDashboard() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [requests, setRequests] = useState([]);
  const [filteredRequests, setFilteredRequests] = useState([]);
  const [filterStatus, setFilterStatus] = useState('ACTIVE');
  const [searchKeyword, setSearchKeyword] = useState('');
  const [searchServiceType, setSearchServiceType] = useState('');
  const [serviceTypes, setServiceTypes] = useState([]);
  const toast = useToast();
  const [completingRequest, setCompletingRequest] = useState(null);
  const [showCompleteModal, setShowCompleteModal] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [completionFeedback, setCompletionFeedback] = useState('');
  const [completionRating, setCompletionRating] = useState('');

  const getToken = () => localStorage.getItem('token');

  useEffect(() => {
    // Check if user is logged in and has PIN role
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
    fetchServiceTypes();
    setLoading(false);
  }, [router]);

  useEffect(() => {
    if (user) {
      fetchRequests();
    }
  }, [user, filterStatus]);

  useEffect(() => {
    applyFilters();
  }, [requests, searchKeyword, searchServiceType]);

  const fetchServiceTypes = async () => {
    try {
      const token = getToken();
      if (!token) return;

      const response = await axios.get(
        'http://localhost:5000/api/requests/service-types',
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Handle if response.data is an array (double-wrapped)
      const actualData = Array.isArray(response.data) ? response.data[0] : response.data;

      if (actualData && actualData.success) {
        setServiceTypes(actualData.data || []);
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
      const effectiveStatus = filterStatus === 'ASSIGNED' ? 'ACTIVE' : filterStatus;
      const response = await axios.get(
        `http://localhost:5000/api/requests?status=${effectiveStatus}`,
        {
          headers: { Authorization: `Bearer ${getToken()}` },
          params: { page: 1, limit: 100 }
        }
      );

      if (response.data.success) {
        const requestsData = response.data.data || [];
        const filteredForAssignment = filterStatus === 'ASSIGNED'
          ? requestsData.filter(req => req.assignment_status === 'IN_PROGRESS')
          : requestsData;
        setRequests(filteredForAssignment);
      } else {
        toast.error(response.data.message || 'Failed to load requests');
      }
    } catch (err) {
      console.error('Failed to fetch requests:', err);
      toast.error('Failed to load requests');
    }
  };

  const openCompleteModal = (request) => {
    setSelectedRequest(request);
    setCompletionFeedback('');
    setCompletionRating('');
    setShowCompleteModal(true);
  };

  const closeCompleteModal = () => {
    setShowCompleteModal(false);
    setSelectedRequest(null);
    setCompletingRequest(null);
    setCompletionFeedback('');
    setCompletionRating('');
  };

  const handleMarkAsCompleted = async () => {
    if (!selectedRequest) return;

    setCompletingRequest(selectedRequest.id);
    try {
      const payload = {
        status: 'FULFILLED',
        feedback_from_pin: completionFeedback || undefined,
        volunteered_hours: completionRating || undefined
      };

      const response = await axios.put(
        `http://localhost:5000/api/requests/${selectedRequest.id}`,
        payload,
        { headers: { Authorization: `Bearer ${getToken()}` } }
      );

      if (response.data.success) {
        toast.success('Request marked as completed!');
        fetchRequests(); // Refresh the list
        closeCompleteModal();
      } else {
        const msg = response.data.message || 'Failed to mark request as completed';
        toast.error(msg);
      }
    } catch (err) {
      console.error('Error marking request as completed:', err);
      const msg = err.response?.data?.message || 'Failed to mark request as completed';
      toast.error(msg);
    } finally {
      setCompletingRequest(null);
    }
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

  const StatusBadge = ({ status }) => {
    const colors = {
      'ACTIVE': 'bg-green-100 text-green-800',
      'SUSPENDED': 'bg-yellow-100 text-yellow-800',
      'FULFILLED': 'bg-blue-100 text-blue-800',
      'CANCELLED': 'bg-red-100 text-red-800'
    };
    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${colors[status] || 'bg-gray-100 text-gray-800'}`}>
        {status}
      </span>
    );
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Header title="PIN Dashboard" subtitle={`Welcome, ${user?.full_name}`} />

      {/* Toast notifications will appear via ToastProvider */}

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <button
            onClick={() => router.push('/pin/request/new')}
            className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white rounded-lg shadow-lg p-6 text-left transition-all duration-200 transform hover:scale-105"
          >
            <div className="text-4xl mb-3">➕</div>
            <h3 className="font-bold text-lg mb-2">Create New Request</h3>
            <p className="text-blue-100 text-sm">Submit a new request for help</p>
          </button>

          <button
            onClick={() => router.push('/pin/history')}
            className="bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white rounded-lg shadow-lg p-6 text-left transition-all duration-200 transform hover:scale-105"
          >
            <div className="text-4xl mb-3">�</div>
            <h3 className="font-bold text-lg mb-2">View History</h3>
            <p className="text-green-100 text-sm">See completed matches</p>
          </button>
        </div>

        {/* Status Filter Tabs */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              <button
                onClick={() => setFilterStatus('ACTIVE')}
                className={`py-4 px-6 text-sm font-medium border-b-2 transition-colors ${
                  filterStatus === 'ACTIVE'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Active
              </button>
              <button
                onClick={() => setFilterStatus('ASSIGNED')}
                className={`py-4 px-6 text-sm font-medium border-b-2 transition-colors ${
                  filterStatus === 'ASSIGNED'
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                In Progress
              </button>
              <button
                onClick={() => setFilterStatus('SUSPENDED')}
                className={`py-4 px-6 text-sm font-medium border-b-2 transition-colors ${
                  filterStatus === 'SUSPENDED'
                    ? 'border-yellow-500 text-yellow-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Suspended
              </button>
              <button
                onClick={() => setFilterStatus('FULFILLED')}
                className={`py-4 px-6 text-sm font-medium border-b-2 transition-colors ${
                  filterStatus === 'FULFILLED'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Fulfilled
              </button>
            </nav>
          </div>

          {/* Search Panel */}
          <div className="p-6">
            <h2 className="text-lg font-semibold mb-4">🔍 Search & Filter</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="md:col-span-2">
                <input
                  type="text"
                  placeholder="Search by title or description..."
                  value={searchKeyword}
                  onChange={(e) => setSearchKeyword(e.target.value)}
                  className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <select
                  value={searchServiceType}
                  onChange={(e) => setSearchServiceType(e.target.value)}
                  className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                  Found {filteredRequests.length} {filteredRequests.length === 1 ? 'request' : 'requests'}
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
        </div>

        {/* All Requests Grid */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-bold text-gray-900">
              {filterStatus === 'ASSIGNED'
                ? 'In Progress Requests'
                : filterStatus.charAt(0) + filterStatus.slice(1).toLowerCase() + ' Requests'}
            </h2>
          </div>
          <div className="p-6">
            <RequestCardGrid
              emptyMessage={`No ${filterStatus === 'ASSIGNED' ? 'in-progress' : filterStatus.toLowerCase()} requests ${searchKeyword || searchServiceType ? 'match your search' : 'yet'}`}
              emptyIcon="📝"
              emptyAction={
                (searchKeyword || searchServiceType) ? (
                  <button
                    onClick={clearFilters}
                    className="mt-4 bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg"
                  >
                    Clear Filters
                  </button>
                ) : (
                  <button
                    onClick={() => router.push('/pin/request/new')}
                    className="mt-4 bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg"
                  >
                    Create Your First Request
                  </button>
                )
              }
            >
              {filteredRequests.map((request) => {
                const assignmentStatus = request.assignment_status;
                const assignedVolunteer = request.active_assignment?.csr_user?.full_name;
                const canMarkCompleted = assignmentStatus === 'IN_PROGRESS';
                return (
                <RequestCard
                  key={request.id}
                  request={request}
                  onClick={() => router.push(`/pin/request/${request.id}`)}
                  theme="blue"
                  extraInfo={
                    <div className="space-y-2">
                      {assignmentStatus ? (
                        <div className="flex items-center text-sm font-medium bg-indigo-50 border border-indigo-200 text-indigo-700 rounded-lg px-3 py-2">
                          <span className="mr-2">🤝</span>
                          <span>
                            {assignmentStatus === 'IN_PROGRESS'
                              ? `In progress with ${assignedVolunteer || 'CSR Volunteer'}`
                              : `Completed by ${assignedVolunteer || 'CSR Volunteer'}`}
                          </span>
                        </div>
                      ) : (
                        <div className="flex items-center text-sm text-green-700 bg-green-50 border border-green-200 rounded-lg px-3 py-2">
                          <span className="mr-2">✅</span>
                          <span>Awaiting CSR assignment</span>
                        </div>
                      )}
                      <div className="flex items-center justify-between text-sm text-gray-600">
                        <div className="flex items-center">
                          <span className="mr-1">👁️</span>
                          <span>{request.view_count || 0} views</span>
                        </div>
                        <div className="flex items-center">
                          <span className="mr-1">⭐</span>
                          <span>{request.shortlist_count || 0} shortlisted</span>
                        </div>
                      </div>
                    </div>
                  }
                  actionButton={
                    <div className="pt-4 border-t space-y-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          router.push(`/pin/request/${request.id}`);
                        }}
                        className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium flex items-center justify-center gap-2"
                      >
                        <span>👁️</span>
                        <span>View Details</span>
                      </button>
                      {request.status === 'ACTIVE' && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            openCompleteModal(request);
                          }}
                          disabled={completingRequest === request.id || !canMarkCompleted}
                          className={`w-full px-4 py-2 rounded-lg font-medium flex items-center justify-center gap-2 ${
                            completingRequest === request.id
                              ? 'bg-gray-300 text-gray-600 cursor-not-allowed'
                              : canMarkCompleted
                                ? 'bg-green-600 text-white hover:bg-green-700 transition-colors'
                                : 'bg-gray-200 text-gray-500 cursor-not-allowed'
                          }`}
                        >
                          <span>✓</span>
                          <span>
                            {completingRequest === request.id
                              ? 'Processing...'
                              : canMarkCompleted
                                ? 'Mark as Completed'
                                : 'Waiting for CSR Progress'}
                          </span>
                        </button>
                      )}
                    </div>
                  }
                />
              );})}
            </RequestCardGrid>
          </div>
        </div>
      </main>

      {showCompleteModal && selectedRequest && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 px-4">
          <div className="bg-white rounded-lg shadow-2xl max-w-lg w-full p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-3">Mark Request as Completed</h2>
            <p className="text-gray-600 mb-4">
              You&apos;re about to mark <span className="font-semibold">{selectedRequest.title}</span> as completed.
            </p>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <p className="text-sm text-blue-700">
                This confirms the CSR volunteer has finished the opportunity. You can still leave feedback later
                from the history tab if needed.
              </p>
            </div>
            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Rate Volunteer (1-5)
                </label>
                <input
                  type="number"
                  min="0"
                  step="0.5"
                  value={completionRating}
                  onChange={(e) => setCompletionRating(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="Rate 1-5"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Feedback for the CSR Rep (optional)
                </label>
                <textarea
                  rows={4}
                  value={completionFeedback}
                  onChange={(e) => setCompletionFeedback(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="Say thanks or share how the volunteering went..."
                />
              </div>
            </div>
            <div className="flex justify-end gap-3">
              <button
                onClick={closeCompleteModal}
                className="px-4 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-100 transition"
              >
                Cancel
              </button>
              <button
                onClick={handleMarkAsCompleted}
                disabled={completingRequest === selectedRequest.id}
                className={`px-4 py-2 rounded-lg text-white font-semibold transition ${
                  completingRequest === selectedRequest.id
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-green-600 hover:bg-green-700'
                }`}
              >
                {completingRequest === selectedRequest.id ? 'Completing...' : 'Yes, mark as completed'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
