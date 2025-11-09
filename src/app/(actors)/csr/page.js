/**
 * CSR Dashboard - Browse and Shortlist PIN Requests (BOUNDARY LAYER - UI)
 * 
 * This component serves as the main dashboard for CSR Representatives to:
 * 1. Browse active PIN requests
 * 2. Add/Remove requests to/from their shortlist
 * 3. Filter and search requests
 * 
 * BCE ARCHITECTURE:
 * - BOUNDARY: This React component (UI/Presentation layer)
 * - CONTROL: Backend Flask controllers handle business logic
 * - ENTITY: Backend entity classes handle database operations
 * 
 * SEQUENCE FLOW (Add to Shortlist):
 * 1. CSR clicks star icon → handleToggleShortlist(requestId)
 * 2. Frontend sends POST to /api/shortlist with JWT token
 * 3. Backend Boundary validates token → calls Control layer
 * 4. Control layer validates request → calls Entity layer
 * 5. Entity layer adds record to database
 * 6. Response flows back: Entity → Control → Boundary → Frontend
 * 7. Frontend updates UI state and re-fetches shortlist
 * 
 * SEQUENCE FLOW (Remove from Shortlist):
 * 1. CSR clicks filled star icon → handleToggleShortlist(requestId)
 * 2. Frontend sends GET to /api/shortlist to find shortlist item ID
 * 3. Frontend sends DELETE to /api/shortlist/{id} with JWT token
 * 4. Backend validates and deletes record
 * 5. Frontend updates UI state
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import Header from '../../components/Header';
import Alert from '../../components/Alert';
import { useToast } from '../../components/ToastProvider';
import RequestCard from '../../components/RequestCard';
import RequestCardGrid from '../../components/RequestCardGrid';

export default function CSRDashboard() {
  // ===== STATE MANAGEMENT =====
  const router = useRouter();
  const [user, setUser] = useState(null);                    // Current logged-in user
  const [loading, setLoading] = useState(true);              // Loading state for initial page load
  const [requests, setRequests] = useState([]);              // All active PIN requests
  const [serviceTypes, setServiceTypes] = useState([]);      // Available service types for filtering
  const [shortlistedIds, setShortlistedIds] = useState([]);  // Array of request IDs that user has shortlisted
  const [error, setError] = useState('');                    // Error message display
  const toast = useToast();
  const [searchKeyword, setSearchKeyword] = useState('');    // Search filter
  const [searchServiceType, setSearchServiceType] = useState(''); // Service type filter
  const [addingToShortlist, setAddingToShortlist] = useState(null); // Track which request is being added/removed

  /**
   * Helper: Get JWT authentication token from localStorage
   * Used in all API calls requiring authentication
   */
  const getToken = () => localStorage.getItem('token');

  /**
   * INITIALIZATION EFFECT
   * Runs on component mount to:
   * 1. Validate user authentication and role
   * 2. Fetch initial data (requests, service types, shortlist)
   * 
   * Security: Redirects to login if no token or wrong role
   */
  useEffect(() => {
    // Check if user is logged in and has CSR Rep role
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
    fetchRequests();
    fetchServiceTypes();
    fetchShortlistedIds();
    setLoading(false);
  }, [router]);

  /**
   * API CALL: Fetch Service Types
   * 
   * ENDPOINT: GET /api/requests/service-types
   * PURPOSE: Load available service types for filter dropdown
   * AUTHENTICATION: Not required (public data)
   * 
   * SEQUENCE:
   * Frontend → Backend Boundary → Backend Control → Backend Entity → Database
   * Response flows back with service types array
   */
  const fetchServiceTypes = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/requests/service-types');
      
      // Handle if response.data is an array (double-wrapped)
      const actualData = Array.isArray(response.data) ? response.data[0] : response.data;
      
      if (actualData && actualData.success) {
        setServiceTypes(actualData.data || []);
      }
    } catch (err) {
      console.error('Failed to fetch service types:', err);
    }
  };

  /**
   * API CALL: Fetch Shortlisted Request IDs
   * 
   * ENDPOINT: GET /api/shortlist
   * PURPOSE: Load IDs of requests the current user has shortlisted
   * AUTHENTICATION: Required (JWT Bearer token)
   * 
   * RESPONSE FORMAT: Backend returns array wrapper
   * [{success: true, data: [{id, request_id, ...}, ...]}]
   * 
   * SEQUENCE:
   * 1. Frontend sends GET with Authorization header
   * 2. Backend Boundary (get_shortlist_boundary.py) receives request
   * 3. Backend Control (get_shortlist_controller.py) validates token
   * 4. Backend Entity (shortlist.py) queries database
   * 5. Response returns shortlist items for current user
   * 6. Frontend extracts request_id values into array
   * 
   * NOTE: Array wrapper fix applied - accesses response.data[0]
   */
  const fetchShortlistedIds = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/shortlist', {
        headers: { 'Authorization': `Bearer ${getToken()}` }
      });
      
      // Backend returns array wrapper - access first element
      const responseData = Array.isArray(response.data) ? response.data[0] : response.data;
      
      if (responseData.success) {
        const ids = responseData.data.map(item => item.request_id);
        setShortlistedIds(ids);
      }
    } catch (err) {
      console.error('[ERROR] Failed to fetch shortlisted IDs:', err);
    }
  };

  /**
   * API CALL: Fetch Active PIN Requests
   * 
   * ENDPOINT: GET /api/requests?status=ACTIVE
   * PURPOSE: Load all active PIN requests for CSR to browse
   * AUTHENTICATION: Required (JWT Bearer token)
   * 
   * SEQUENCE:
   * Frontend → Backend Boundary → Backend Control → Backend Entity → Database
   * Returns all requests with status='ACTIVE'
   */
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

  /**
   * MAIN SHORTLIST TOGGLE HANDLER
   * 
   * PURPOSE: Add or remove a request from the user's shortlist
   * TRIGGERED BY: User clicking the star icon on a request card
   * 
   * SEQUENCE DIAGRAM FLOW:
   * 
   * [ADD TO SHORTLIST]
   * 1. User clicks outline star (☆)
   * 2. handleToggleShortlist(requestId) called
   * 3. Check: isCurrentlyShortlisted = false
   * 4. POST /api/shortlist with {request_id: requestId}
   * 5. Backend Boundary: add_to_shortlist_boundary.py receives request
   * 6. Backend Control: add_to_shortlist_controller.py validates
   * 7. Backend Entity: shortlist.py adds record to database
   * 8. Frontend receives success response
   * 9. Update state: add requestId to shortlistedIds array
   * 10. Re-fetch shortlist to sync with database
   * 11. UI updates: star becomes filled (⭐), purple badge appears
   * 
   * [REMOVE FROM SHORTLIST]
   * 1. User clicks filled star (⭐)
   * 2. handleToggleShortlist(requestId) called
   * 3. Check: isCurrentlyShortlisted = true
   * 4. GET /api/shortlist to find the shortlist item ID
   * 5. Find matching item: item.request_id === requestId
   * 6. DELETE /api/shortlist/{shortlistItemId}
   * 7. Backend Boundary: remove_from_shortlist_boundary.py receives request
   * 8. Backend Control: remove_from_shortlist_controller.py validates
   * 9. Backend Entity: shortlist.py deletes record from database
   * 10. Frontend receives success response
   * 11. Update state: remove requestId from shortlistedIds array
   * 12. Re-fetch shortlist to sync with database
   * 13. UI updates: star becomes outline (☆), badge removed
   * 
   * @param {number} requestId - The ID of the request to add/remove from shortlist
   */
  const handleToggleShortlist = async (requestId) => {
    const isCurrentlyShortlisted = shortlistedIds.includes(requestId);
    const targetRequest = requests.find(r => r.id === requestId);
    if (!isCurrentlyShortlisted && targetRequest?.active_assignment && targetRequest.active_assignment.csr_user_id !== user?.id) {
      toast.error('This opportunity has already been accepted by another CSR representative.');
      return;
    }

    setAddingToShortlist(requestId);
    setError('');

    try {
      if (isCurrentlyShortlisted) {
        // ===== REMOVE FROM SHORTLIST =====
        // Step 1: Fetch all shortlist items to find the specific item ID
        const shortlistResponse = await axios.get('http://localhost:5000/api/shortlist', {
          headers: { 'Authorization': `Bearer ${getToken()}` }
        });
        
        // Fix: Backend returns array wrapper
        const responseData = Array.isArray(shortlistResponse.data) ? shortlistResponse.data[0] : shortlistResponse.data;
        const shortlistItem = responseData.data.find(item => item.request_id === requestId);
        
        if (shortlistItem) {
          // Step 2: Delete the shortlist item using its ID
          await axios.delete(`http://localhost:5000/api/shortlist/${shortlistItem.id}`, {
            headers: { 'Authorization': `Bearer ${getToken()}` }
          });
          
          // Step 3: Update UI state immediately (optimistic update)
          setShortlistedIds(prev => prev.filter(id => id !== requestId));
          toast.success('Removed from shortlist');
        } else {
          setError('Could not find shortlist item');
        }
      } else {
        // ===== ADD TO SHORTLIST =====
        // Step 1: Send POST request with request_id
        await axios.post('http://localhost:5000/api/shortlist', 
          { request_id: requestId },
          { headers: { 'Authorization': `Bearer ${getToken()}` } }
        );
        
  // Step 2: Update UI state immediately (optimistic update)
  setShortlistedIds(prev => [...prev, requestId]);
  toast.success('Added to shortlist');
      }
      
      // Step 3: Re-fetch from server to ensure UI matches database
      await fetchShortlistedIds();
      await fetchRequests();
    } catch (err) {
      console.error('Shortlist toggle error:', err);
      const msg = err.response?.data?.message || 'Failed to update shortlist';
      setError(msg);
      toast.error(msg);
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

      {/* transient success messages are shown via the global toast */}

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
            const activeAssignment = request.active_assignment;
            const takenByOther = activeAssignment && activeAssignment.csr_user_id !== user?.id;
            const takenByMe = activeAssignment && activeAssignment.csr_user_id === user?.id;
            const takenByName = activeAssignment?.csr_user?.full_name;
            return (
              <RequestCard
                key={request.id}
                request={request}
                onClick={() => router.push(`/csr/browse/${request.id}`)}
                theme="purple"
                badge={
                  <>
                    {request.assignment_status === 'IN_PROGRESS' && (
                      <div className="absolute top-3 left-3 bg-blue-600 text-white px-3 py-1 rounded-full text-xs font-semibold shadow-lg flex items-center gap-2 z-10">
                        <span>🚀</span>
                        <span>{takenByMe ? 'In Progress (You)' : 'In Progress'}</span>
                      </div>
                    )}
                    {request.assignment_status === 'COMPLETED' && (
                      <div className="absolute top-3 left-3 bg-green-600 text-white px-3 py-1 rounded-full text-xs font-semibold shadow-lg flex items-center gap-2 z-10">
                        <span>✅</span>
                        <span>Completed</span>
                      </div>
                    )}
                    {isShortlisted && (
                      <div className="absolute top-3 right-3 bg-purple-600 text-white px-3 py-1 rounded-full text-xs font-semibold shadow-lg flex items-center gap-1 z-10">
                        <span>⭐</span>
                        <span>Shortlisted</span>
                      </div>
                    )}
                  </>
                }
                extraInfo={activeAssignment ? (
                  <div className="flex items-center text-sm font-medium text-purple-700 bg-purple-50 border border-purple-200 rounded-lg px-3 py-2">
                    <span className="mr-2">👤</span>
                    <span>
                      {takenByMe ? 'You are currently volunteering for this opportunity.' : `Claimed by ${takenByName}.`}
                    </span>
                  </div>
                ) : null}
                actionButton={
                  <div className="flex items-center justify-between pt-4 border-t">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleToggleShortlist(request.id);
                      }}
                      disabled={addingToShortlist === request.id || (takenByOther && !isShortlisted)}
                      className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-all ${
                        isShortlisted 
                          ? 'bg-purple-100 text-purple-700 hover:bg-purple-200' 
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      } ${(addingToShortlist === request.id || (takenByOther && !isShortlisted)) ? 'opacity-50 cursor-not-allowed' : ''}`}
                      title={
                        takenByOther && !isShortlisted 
                          ? `Taken by ${takenByName}`
                          : (isShortlisted ? 'Remove from shortlist' : 'Add to shortlist')
                      }
                    >
                      <span className="text-xl">{isShortlisted ? '⭐' : '☆'}</span>
                      <span className="text-sm font-medium">
                        {addingToShortlist === request.id
                          ? 'Processing...'
                          : takenByOther && !isShortlisted
                            ? `Taken by ${takenByName}`
                            : (isShortlisted ? 'Shortlisted' : 'Shortlist')}
                      </span>
                    </button>
                    <button
                      onClick={() => router.push(`/csr/browse/${request.id}`)}
                      className="flex-1 ml-3 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-medium"
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
