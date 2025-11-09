'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import axios from 'axios';
import Header from '../../../../components/Header';
import Alert from '../../../../components/Alert';
import { useToast } from '../../../../components/ToastProvider';

export default function CSRViewRequestDetail() {
  const router = useRouter();
  const params = useParams();
  const requestId = params.id;

  const [user, setUser] = useState(null);
  const [request, setRequest] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const toast = useToast();
  const [isShortlisted, setIsShortlisted] = useState(false);
  const [addingToShortlist, setAddingToShortlist] = useState(false);

  const isTakenByAnotherCSR = request?.active_assignment 
    && request.active_assignment.csr_user_id 
    && request.active_assignment.csr_user_id !== user?.id;

  const takenByName = request?.active_assignment?.csr_user?.full_name;

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
    fetchRequestDetail();
    checkIfShortlisted();
  }, [requestId]);

  const fetchRequestDetail = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`http://localhost:5000/api/requests/${requestId}`, {
        headers: { 'Authorization': `Bearer ${getToken()}` }
      });

      if (response.data.success) {
        setRequest(response.data.data);
      } else {
        setError(response.data.message || 'Failed to load request details');
      }
    } catch (err) {
      console.error('Error fetching request:', err);
      setError('Failed to load request details');
    } finally {
      setLoading(false);
    }
  };

  const checkIfShortlisted = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/shortlist', {
        headers: { 'Authorization': `Bearer ${getToken()}` }
      });
      
      // Handle if response.data is an array (double-wrapped)
      const actualData = Array.isArray(response.data) ? response.data[0] : response.data;
      
      if (actualData && actualData.success) {
        const shortlisted = actualData.data.some(item => item.request_id === parseInt(requestId));
        setIsShortlisted(shortlisted);
      }
    } catch (err) {
      console.error('Failed to check shortlist status:', err);
    }
  };

  const handleToggleShortlist = async () => {
    if (!isShortlisted && isTakenByAnotherCSR) {
      toast.error('This opportunity has already been accepted by another CSR representative.');
      return;
    }

    setAddingToShortlist(true);
    try {
      if (isShortlisted) {
        // Remove from shortlist - need to get the shortlist item ID first
        const response = await axios.get('http://localhost:5000/api/shortlist', {
          headers: { 'Authorization': `Bearer ${getToken()}` }
        });
        
        // Handle array wrapper
        const actualData = Array.isArray(response.data) ? response.data[0] : response.data;
        
        if (actualData && actualData.success) {
          const shortlistItem = actualData.data.find(item => item.request_id === parseInt(requestId));
          
          if (shortlistItem) {
            await axios.delete(`http://localhost:5000/api/shortlist/${shortlistItem.id}`, {
              headers: { 'Authorization': `Bearer ${getToken()}` }
            });
            setIsShortlisted(false);
            toast.success('Removed from shortlist');
          }
        }
      } else {
        // Add to shortlist
        await axios.post('http://localhost:5000/api/shortlist', 
          { request_id: parseInt(requestId) },
          { headers: { 'Authorization': `Bearer ${getToken()}` } }
        );
        setIsShortlisted(true);
        toast.success('Added to shortlist');
      }
      
      await fetchRequestDetail();
      await checkIfShortlisted();
    } catch (err) {
        const msg = err.response?.data?.message || 'Failed to update shortlist';
        toast.error(msg);
    } finally {
      setAddingToShortlist(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-100">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mb-4"></div>
          <p className="text-gray-600">Loading request details...</p>
        </div>
      </div>
    );
  }

  if (error && !request) {
    return (
      <div className="min-h-screen bg-gray-100">
        <Header title="Request Not Found" subtitle="CSR Rep Dashboard" />
        <div className="max-w-4xl mx-auto px-4 py-8">
          <Alert type="error" message={error} onClose={() => router.push('/csr')} />
          <button
            onClick={() => router.push('/csr')}
            className="mt-4 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
          >
            ← Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <Header title="Request Details" subtitle="Volunteering Opportunity" />

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-4">
            <Alert type="error" message={error} onClose={() => setError('')} />
          </div>
        )}

        {/* success messages now shown via global toast */}

        {/* Back Button and Shortlist Link */}
        <div className="mb-6 flex items-center justify-between">
          <button
            onClick={() => router.push('/csr')}
            className="flex items-center text-purple-600 hover:text-purple-700 font-medium"
          >
            <span className="mr-2">←</span> Back to Dashboard
          </button>
          
          <button
            onClick={() => router.push('/csr/shortlist')}
            className="flex items-center text-purple-600 hover:text-purple-700 font-medium"
          >
            <span className="mr-2">📋</span> View My Shortlist
          </button>
        </div>

        {/* Request Details Card */}
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          {/* Header with Status */}
          <div className="bg-gradient-to-r from-purple-600 to-purple-700 px-6 py-4 text-white">
            <div className="flex items-center justify-between">
              <h1 className="text-2xl font-bold">{request?.title}</h1>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                request?.status === 'ACTIVE' ? 'bg-green-500' :
                request?.status === 'SUSPENDED' ? 'bg-yellow-500' :
                request?.status === 'FULFILLED' ? 'bg-blue-500' :
                'bg-gray-500'
              }`}>
                {request?.status}
              </span>
            </div>
          </div>

          {/* Request Image */}
          {request?.image_url && (
            <div className="w-full h-64 bg-gray-200">
              <img
                src={request.image_url}
                alt={request.title}
                className="w-full h-full object-cover"
              />
            </div>
          )}

          {/* Request Info */}
          <div className="p-6 space-y-6">
            {/* Description */}
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-2">Description</h2>
              <p className="text-gray-700 whitespace-pre-wrap">{request?.description}</p>
            </div>

            {/* Details Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t">
              <div>
                <p className="text-sm text-gray-600">Service Type</p>
                <p className="font-medium text-gray-900">{request?.service_type || 'Not specified'}</p>
              </div>

              <div>
                <p className="text-sm text-gray-600">Location</p>
                <p className="font-medium text-gray-900">{request?.region || 'Not specified'}</p>
              </div>

              <div>
                <p className="text-sm text-gray-600">Assigned CSR Volunteer</p>
                <p className="font-medium text-gray-900">
                  {takenByName ? `${takenByName}${request?.active_assignment?.status === 'IN_PROGRESS' ? ' (In Progress)' : ''}` : 'Not yet accepted'}
                </p>
              </div>

              <div>
                <p className="text-sm text-gray-600">Posted Date</p>
                <p className="font-medium text-gray-900">
                  {request?.created_at 
                    ? new Date(request.created_at).toLocaleDateString()
                    : 'Unknown'}
                </p>
              </div>
            </div>

            {/* Additional Info */}
            {request?.additional_info && (
              <div className="pt-4 border-t">
                <h2 className="text-lg font-semibold text-gray-900 mb-2">Additional Information</h2>
                <p className="text-gray-700 whitespace-pre-wrap">{request.additional_info}</p>
              </div>
            )}

            {/* Action Buttons */}
            <div className="pt-6 border-t">
              <button
                onClick={handleToggleShortlist}
                disabled={addingToShortlist || (isTakenByAnotherCSR && !isShortlisted)}
                className={`w-full px-6 py-3 rounded-lg font-medium transition-colors ${
                  isTakenByAnotherCSR && !isShortlisted
                    ? 'bg-gray-400 text-white cursor-not-allowed'
                    : isShortlisted
                      ? 'bg-red-600 hover:bg-red-700 text-white'
                      : 'bg-purple-600 hover:bg-purple-700 text-white'
                } ${(addingToShortlist || (isTakenByAnotherCSR && !isShortlisted)) ? 'opacity-70 cursor-not-allowed' : ''}`}
              >
                {addingToShortlist
                  ? 'Processing...'
                  : isShortlisted
                    ? '❤️ Remove from Shortlist'
                    : isTakenByAnotherCSR
                      ? `Taken by ${takenByName}`
                      : '🤍 Add to Shortlist'}
              </button>

              {isTakenByAnotherCSR && (
                <p className="mt-3 text-sm text-purple-700 bg-purple-100 border border-purple-200 rounded-lg p-3">
                  This opportunity is currently being handled by {takenByName}. Please choose another request.
                </p>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
