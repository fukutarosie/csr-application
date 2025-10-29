'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function NewRequest() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: '',
    service_type: '',
    priority: 'MEDIUM',
    location_city: '',
    location_detail: '',
    requested_by_date: '',
  });

  const [categories, setCategories] = useState([]);
  const [serviceTypes, setServiceTypes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    fetchLookupData();
  }, []);

  const fetchLookupData = async () => {
    try {
      const token = localStorage.getItem('token');
      
      // Fetch categories
      const categoriesRes = await axios.get(
        'http://localhost:5000/api/lookup/categories',
        { headers: { Authorization: `Bearer ${token}` } }
      );
      if (categoriesRes.data.success) {
        setCategories(categoriesRes.data.data || []);
      }

      // Fetch service types
      const typesRes = await axios.get(
        'http://localhost:5000/api/lookup/service-types',
        { headers: { Authorization: `Bearer ${token}` } }
      );
      if (typesRes.data.success) {
        setServiceTypes(typesRes.data.data || []);
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

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        setError('Not authenticated');
        return;
      }

      const response = await axios.post(
        'http://localhost:5000/api/requests',
        formData,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.data.success) {
        setSuccess(true);
        setFormData({
          title: '',
          description: '',
          category: '',
          service_type: '',
          priority: 'MEDIUM',
          location_city: '',
          location_detail: '',
          requested_by_date: '',
        });

        // Redirect after success
        setTimeout(() => {
          router.push(`/pin/request/${response.data.data.id}`);
        }, 1500);
      } else {
        setError(response.data.message);
      }
    } catch (err) {
      setError(err.response?.data?.message || err.message);
      console.error('Error creating request:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Link href="/pin/dashboard">
            <button className="text-blue-600 hover:text-blue-800 font-semibold mb-4">
              ← Back to Dashboard
            </button>
          </Link>
          <h1 className="text-4xl font-bold text-gray-800">Create New Request</h1>
          <p className="text-gray-600 mt-2">Fill in the details about your service request</p>
        </div>

        {/* Success Message */}
        {success && (
          <div className="mb-6 p-4 bg-green-50 border-l-4 border-green-500 rounded">
            <p className="text-green-700 font-semibold">Request created successfully!</p>
            <p className="text-green-600 text-sm">Redirecting...</p>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-500 rounded">
            <p className="text-red-700 font-semibold">Error</p>
            <p className="text-red-600">{error}</p>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-lg p-8">
          {/* Title */}
          <div className="mb-6">
            <label className="block text-gray-700 font-semibold mb-2">
              Request Title *
            </label>
            <input
              type="text"
              name="title"
              value={formData.title}
              onChange={handleChange}
              placeholder="Brief title of your request"
              required
              minLength="5"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
            />
            <p className="text-gray-500 text-xs mt-1">Minimum 5 characters</p>
          </div>

          {/* Description */}
          <div className="mb-6">
            <label className="block text-gray-700 font-semibold mb-2">
              Description *
            </label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Provide details about your request"
              required
              minLength="10"
              rows="5"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
            />
            <p className="text-gray-500 text-xs mt-1">Minimum 10 characters</p>
          </div>

          {/* Two Column Layout */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            {/* Category */}
            <div>
              <label className="block text-gray-700 font-semibold mb-2">
                Category *
              </label>
              <select
                name="category"
                value={formData.category}
                onChange={handleChange}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
              >
                <option value="">Select category</option>
                {categories.map(cat => (
                  <option key={cat.id} value={cat.name}>
                    {cat.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Service Type */}
            <div>
              <label className="block text-gray-700 font-semibold mb-2">
                Service Type
              </label>
              <select
                name="service_type"
                value={formData.service_type}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
              >
                <option value="">Select service type</option>
                {serviceTypes.map(type => (
                  <option key={type.id} value={type.name}>
                    {type.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Priority & Location City */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            {/* Priority */}
            <div>
              <label className="block text-gray-700 font-semibold mb-2">
                Priority
              </label>
              <select
                name="priority"
                value={formData.priority}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
              >
                <option value="LOW">Low</option>
                <option value="MEDIUM">Medium</option>
                <option value="HIGH">High</option>
                <option value="URGENT">Urgent</option>
              </select>
            </div>

            {/* Location City */}
            <div>
              <label className="block text-gray-700 font-semibold mb-2">
                Location (City)
              </label>
              <input
                type="text"
                name="location_city"
                value={formData.location_city}
                onChange={handleChange}
                placeholder="e.g., Bangkok"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
              />
            </div>
          </div>

          {/* Location Detail */}
          <div className="mb-6">
            <label className="block text-gray-700 font-semibold mb-2">
              Location Details
            </label>
            <input
              type="text"
              name="location_detail"
              value={formData.location_detail}
              onChange={handleChange}
              placeholder="Street, building, or area details"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
            />
          </div>

          {/* Requested By Date */}
          <div className="mb-8">
            <label className="block text-gray-700 font-semibold mb-2">
              Requested By Date
            </label>
            <input
              type="date"
              name="requested_by_date"
              value={formData.requested_by_date}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
            />
          </div>

          {/* Buttons */}
          <div className="flex gap-4">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-bold py-3 rounded-lg transition"
            >
              {loading ? 'Creating...' : 'Create Request'}
            </button>
            <Link href="/pin/dashboard" className="flex-1">
              <button
                type="button"
                className="w-full bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-3 rounded-lg transition"
              >
                Cancel
              </button>
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}
