'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import Header from '../../../../components/Header';

export default function NewRequest() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    service_type: '',
    region: '',
    requested_by_date: '',
    image: '',
  });

  const [serviceTypes, setServiceTypes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [imagePreview, setImagePreview] = useState(null);

  useEffect(() => {
    fetchLookupData();
  }, []);

  const fetchLookupData = async () => {
    try {
      console.log('Fetching service types...');
      // Fetch service types (no auth required for lookups)
      const typesRes = await axios.get(
        'http://localhost:5000/api/requests/service-types'
      );
      console.log('Service types response:', typesRes.data);
      
      // Handle if response.data is an array (double-wrapped)
      const actualData = Array.isArray(typesRes.data) ? typesRes.data[0] : typesRes.data;
      console.log('Actual data:', actualData);
      
      if (actualData && actualData.success) {
        console.log('Service types data:', actualData.data);
        setServiceTypes(actualData.data || []);
      }
    } catch (err) {
      console.error('Error fetching lookup data:', err);
      console.error('Error details:', err.response?.data);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    
    if (!file) {
      return;
    }

    // Validate file type
    const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      setError('Please select a valid image file (PNG, JPG, GIF, or WEBP)');
      return;
    }

    // Validate file size (5MB max)
    const maxSize = 5 * 1024 * 1024; // 5MB in bytes
    if (file.size > maxSize) {
      setError('Image file size must be less than 5MB');
      return;
    }

    // Create preview
    const reader = new FileReader();
    
    reader.onloadend = () => {
      const base64String = reader.result;
      setFormData(prev => ({
        ...prev,
        image: base64String
      }));
      setImagePreview(base64String);
      setError(null);
    };

    reader.onerror = () => {
      setError('Failed to read image file');
    };

    reader.readAsDataURL(file);
  };

  const removeImage = () => {
    setFormData(prev => ({
      ...prev,
      image: ''
    }));
    setImagePreview(null);
    // Reset file input
    const fileInput = document.getElementById('imageInput');
    if (fileInput) {
      fileInput.value = '';
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        setError('Not authenticated');
        setLoading(false);
        return;
      }

      // Validate all required fields
      if (!formData.title || !formData.description || !formData.service_type || 
          !formData.region || !formData.requested_by_date || !formData.image) {
        setError('All fields are required, including an image');
        setLoading(false);
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
        // Get the newly created request ID
        const newRequestId = response.data.data?.id;
        
        // Redirect immediately to dashboard (success message will show there)
        if (newRequestId) {
          router.push(`/pin/dashboard?new=${newRequestId}`);
        } else {
          router.push('/pin/dashboard');
        }
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
    <div className="min-h-screen bg-gray-100">
      <Header title="Create New Request" subtitle="Fill in the details about your service request" />
      
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Back Button */}
        <Link href="/pin/dashboard">
          <button className="text-blue-600 hover:text-blue-800 font-semibold mb-6">
            ← Back to Dashboard
          </button>
        </Link>

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

          {/* Service Type and Region */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            {/* Service Type */}
            <div>
              <label className="block text-gray-700 font-semibold mb-2">
                Service Type *
              </label>
              <select
                name="service_type"
                value={formData.service_type}
                onChange={handleChange}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
              >
                <option value="">Select service type</option>
                {serviceTypes.map(type => (
                  <option key={type.id} value={type.service_name}>
                    {type.service_name}
                  </option>
                ))}
              </select>
            </div>

            {/* Region */}
            <div>
              <label className="block text-gray-700 font-semibold mb-2">
                Region *
              </label>
              <input
                type="text"
                name="region"
                value={formData.region}
                onChange={handleChange}
                placeholder="e.g., Hougang, Sengkang, Bugis"
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
              />
            </div>
          </div>

          {/* Requested By Date */}
          <div className="mb-6">
            <label className="block text-gray-700 font-semibold mb-2">
              Requested By Date *
            </label>
            <input
              type="date"
              name="requested_by_date"
              value={formData.requested_by_date}
              onChange={handleChange}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
            />
          </div>

          {/* Image Upload */}
          <div className="mb-8">
            <label className="block text-gray-700 font-semibold mb-2">
              Upload Image *
            </label>
            <p className="text-gray-500 text-sm mb-3">
              Add a photo to help volunteers understand your request (required)
            </p>
            
            {!imagePreview && (
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-400 transition">
                <input
                  id="imageInput"
                  type="file"
                  accept="image/png,image/jpeg,image/jpg,image/gif,image/webp"
                  onChange={handleImageChange}
                  className="hidden"
                />
                <label htmlFor="imageInput" className="cursor-pointer">
                  <div className="flex flex-col items-center">
                    <svg className="w-12 h-12 text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <p className="text-gray-600 font-semibold mb-1">Click to upload image</p>
                    <p className="text-gray-400 text-xs">PNG, JPG, GIF or WEBP (Max 5MB)</p>
                  </div>
                </label>
              </div>
            )}

            {imagePreview && (
              <div className="relative border-2 border-gray-200 rounded-lg p-4">
                <img 
                  src={imagePreview} 
                  alt="Preview" 
                  className="w-full max-h-96 object-contain rounded"
                />
                <button
                  type="button"
                  onClick={removeImage}
                  className="absolute top-2 right-2 bg-red-500 hover:bg-red-600 text-white rounded-full p-2 shadow-lg transition"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
                <p className="text-gray-600 text-sm mt-2 text-center">Image ready for upload</p>
              </div>
            )}
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
