'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import Header from '../../components/Header';
import Alert from '../../components/Alert';
import { useToast } from '../../components/ToastProvider';

export default function UserAdminDashboard() {
  const router = useRouter();
  const [users, setUsers] = useState([]);
  const [filteredUsers, setFilteredUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const toast = useToast();
  const [activeTab, setActiveTab] = useState('users'); // users, profiles
  const [searchTab, setSearchTab] = useState('view'); // view, manage (sub-tabs for users tab)
  const [searchQuery, setSearchQuery] = useState('');

  // Form states
  const [createForm, setCreateForm] = useState({
    username: '',
    password: '',
    email: '',
    full_name: '',
    role_id: ''
  });

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showCreateProfileModal, setShowCreateProfileModal] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [editingProfile, setEditingProfile] = useState(null);
  const [editForm, setEditForm] = useState({
    email: '',
    full_name: '',
    role_id: ''
  });

  const [profiles, setProfiles] = useState([]);
  const [filteredProfiles, setFilteredProfiles] = useState([]);
  const [searchProfileQuery, setSearchProfileQuery] = useState('');
  const [profileForm, setProfileForm] = useState({
    role_name: '',
    role_code: '',
    description: ''
  });
  const [editProfileForm, setEditProfileForm] = useState({
    role_name: '',
    role_code: '',
    description: '',
    dashboard_route: ''
  });

  const [roles, setRoles] = useState([]);

  // Get token from localStorage
  const getToken = () => localStorage.getItem('token');

  // Auto-dismiss error messages after 3 seconds (successes use global toast)
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => {
        setError('');
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  // Fetch users on component mount
  useEffect(() => {
    fetchUsers();
    fetchProfiles();
    fetchRoles();
  }, []);

  const fetchUsers = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await axios.get('http://localhost:5000/api/userAccount', {
        headers: {
          'Authorization': `Bearer ${getToken()}`
        }
      });

      if (response.data.success) {
        setUsers(response.data.data);
        setFilteredUsers(response.data.data);
      }
    } catch (err) {
      const msg = 'Failed to fetch users';
      setError(msg);
      toast.error(msg);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchRoles = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/userProfile', {
        headers: {
          'Authorization': `Bearer ${getToken()}`
        }
      });

      if (response.data.success) {
        setRoles(response.data.data);
      }
    } catch (err) {
      console.error('Failed to fetch roles:', err);
    }
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Call backend API to create user
      const response = await axios.post('http://localhost:5000/api/userAccount', createForm, {
        headers: {
          'Authorization': `Bearer ${getToken()}`
        }
      });
      
      if (response.data.success) {
          toast.success('User created successfully');
        setCreateForm({username: '', password: '', email: '', full_name: '', role_id: ''});
        setShowCreateModal(false);
        await fetchUsers();
      }
    } catch (err) {
        const msg = err.response?.data?.message || 'Failed to create user';
        setError(msg);
        toast.error(msg);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      // Search across all fields (username, email, full_name)
      const results = users.filter(user =>
        user.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
        user.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
        user.full_name.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setFilteredUsers(results);
    } catch (err) {
      setError('Failed to search users');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateUser = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await axios.put(`http://localhost:5000/api/userAccount/${editingUser.id}`, editForm, {
        headers: {
          'Authorization': `Bearer ${getToken()}`
        }
      });

      if (response.data.success) {
        toast.success('User updated successfully');
        setEditingUser(null);
        setTimeout(() => fetchUsers(), 1000);
      } else {
        const msg = response.data.message || 'Failed to update user';
        setError(msg);
        toast.error(msg);
      }
    } catch (err) {
      const msg = err.response?.data?.message || 'Failed to update user';
      setError(msg);
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleSuspendUser = async (userId) => {
    // Optimistic UI update - update table immediately without reload
    setUsers(users.map(user => 
      user.id === userId ? {...user, is_active: false} : user
    ));
    setFilteredUsers(filteredUsers.map(user => 
      user.id === userId ? {...user, is_active: false} : user
    ));
    
    toast.success('User suspended successfully');
    
    // Background API call - don't reload on success or failure
    try {
      await axios.put(`http://localhost:5000/api/userAccount/${userId}/suspend`, {}, {
        headers: {
          'Authorization': `Bearer ${getToken()}`
        }
      });
    } catch (err) {
      // If API fails, revert the optimistic update
      const msg = 'Failed to suspend user';
      setError(msg);
      toast.error(msg);
      fetchUsers(); // Revert to original state
    }
  };

  const handleActivateUser = async (userId) => {
    // Optimistic UI update - update table immediately without reload
    setUsers(users.map(user => 
      user.id === userId ? {...user, is_active: true} : user
    ));
    setFilteredUsers(filteredUsers.map(user => 
      user.id === userId ? {...user, is_active: true} : user
    ));
    
    toast.success('User activated successfully');
    
    // Background API call - don't reload on success or failure
    try {
      await axios.put(`http://localhost:5000/api/userAccount/${userId}/activate`, {}, {
        headers: {
          'Authorization': `Bearer ${getToken()}`
        }
      });
    } catch (err) {
      // If API fails, revert the optimistic update
      const msg = 'Failed to activate user';
      setError(msg);
      toast.error(msg);
      fetchUsers(); // Revert to original state
    }
  };

  const getRoleName = (roleId) => {
    const role = roles.find(r => r.id === roleId);
    return role ? role.role_name : 'Unknown';
  };

  // User Profile Functions (Uses Roles Table)
  const fetchProfiles = async () => {
    setLoading(true);
    setError('');
    try {
      // Profiles are actually the roles table
      const response = await axios.get('http://localhost:5000/api/userProfile', {
        headers: {
          'Authorization': `Bearer ${getToken()}`
        }
      });

      if (response.data.success) {
        setProfiles(response.data.data);
        setFilteredProfiles(response.data.data);
      }
    } catch (err) {
      const msg = 'Failed to fetch profiles';
      setError(msg);
      toast.error(msg);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProfile = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await axios.post('http://localhost:5000/api/userProfile', profileForm, {
        headers: {
          'Authorization': `Bearer ${getToken()}`
        }
      });
      
      if (response.data.success) {
        toast.success('Profile created successfully');
        setProfileForm({ role_name: '', role_code: '', description: '' });
        setShowCreateProfileModal(false);
        await fetchProfiles();
      }
    } catch (err) {
      const msg = err.response?.data?.message || 'Failed to create profile';
      setError(msg);
      toast.error(msg);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const response = await axios.put(
        `http://localhost:5000/api/userProfile/${editingProfile.id}`,
        editProfileForm,
        {
          headers: {
            'Authorization': `Bearer ${getToken()}`
          }
        }
      );
      
      if (response.data.success) {
        toast.success('Profile updated successfully');
        setEditingProfile(null);
        await fetchProfiles();
      }
    } catch (err) {
      const msg = err.response?.data?.message || 'Failed to update profile';
      setError(msg);
      toast.error(msg);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteProfile = async (profileId) => {
    // Find profile to get name
    const profileToDelete = profiles.find(p => p.id === profileId);
    const usersWithThisProfile = users.filter(u => u.role_id === profileId);
    
    // Warning message with cascading info
    const warningMessage = usersWithThisProfile.length > 0
      ? `Are you sure you want to delete "${profileToDelete?.role_name}"? This will also delete ${usersWithThisProfile.length} user account(s) associated with this profile.`
      : `Are you sure you want to delete "${profileToDelete?.role_name}"?`;
    
    if (!window.confirm(warningMessage)) return;
    
    setLoading(true);
    setError('');
    try {
      // Delete from backend (cascading happens in backend)
      const response = await axios.delete(`http://localhost:5000/api/userProfile/${profileId}/delete`, {
        headers: {
          'Authorization': `Bearer ${getToken()}`
        }
      });
      
      if (response.data.success) {
        // Refresh both users and profiles
        await fetchUsers();
        await fetchProfiles();
        
        if (usersWithThisProfile.length > 0) {
          toast.success(`Profile deleted successfully. ${usersWithThisProfile.length} associated user account(s) were also deleted.`);
        } else {
          toast.success('Profile deleted successfully');
        }
      }
    } catch (err) {
      const msg = err.response?.data?.message || 'Failed to delete profile';
      setError(msg);
      toast.error(msg);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchProfiles = async (e) => {
    e.preventDefault();
    try {
      const results = profiles.filter(profile =>
        profile.role_name.toLowerCase().includes(searchProfileQuery.toLowerCase()) ||
        profile.role_code.toLowerCase().includes(searchProfileQuery.toLowerCase()) ||
        profile.description.toLowerCase().includes(searchProfileQuery.toLowerCase())
      );
      setFilteredProfiles(results);
    } catch (err) {
      setError('Failed to search profiles');
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Header title="User Admin Dashboard" />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
  <Alert type="error" message={error} />
  {/* success messages are shown via global toast */}

        {/* Main Tabs */}
        <div className="mb-8 border-b border-gray-200">
          <div className="flex space-x-8">
            <button
              onClick={() => setActiveTab('users')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'users'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              User Account
            </button>
            <button
              onClick={() => setActiveTab('profiles')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'profiles'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              User Profiles
            </button>
          </div>
        </div>

        {/* User Management Tab */}
        {activeTab === 'users' && (
          <div className="space-y-4">
            {/* Create Button and Search Section */}
            <div className="bg-white rounded-lg shadow p-4">
              <h2 className="text-xl font-bold text-gray-900 mb-4">User Account</h2>

              {/* Search Filter - Single Unified Search Box */}
              <div className="flex gap-2">
                <div className="flex-1">
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => {
                      setSearchQuery(e.target.value);
                      if (e.target.value === '') {
                        setFilteredUsers(users);
                      }
                    }}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        handleSearch(e);
                      }
                    }}
                    placeholder="Search by email, username, or full name"
                    className="w-full px-3 py-1.5 border border-gray-300 rounded-lg shadow-sm text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <button
                  onClick={handleSearch}
                  className="px-4 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium text-sm"
                >
                  Search
                </button>
                <button
                  onClick={() => {
                    fetchRoles();
                    fetchProfiles();
                    setShowCreateModal(true);
                  }}
                  className="px-4 py-1.5 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-medium text-sm"
                >
                  + Add New User
                </button>
              </div>
            </div>

            {/* View Users Table */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-4 py-3">
                <h2 className="text-lg font-bold text-gray-900 mb-4">All Users</h2>
                {loading ? (
                  <p className="text-center text-gray-500 py-4 text-sm">Loading...</p>
                ) : filteredUsers.length === 0 ? (
                  <p className="text-center text-gray-500 py-4 text-sm">No users found</p>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Username</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Full Name</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {filteredUsers.map((user) => (
                          <tr key={user.id} className="hover:bg-gray-50">
                            <td className="px-4 py-2 whitespace-nowrap text-sm font-medium text-gray-900">{user.username}</td>
                            <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-600">{user.email}</td>
                            <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-600">{user.full_name}</td>
                            <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-600">{getRoleName(user.role_id)}</td>
                            <td className="px-4 py-2 whitespace-nowrap">
                              <span className={`px-2 py-0.5 inline-flex text-xs leading-5 font-semibold rounded-full ${
                                user.is_active
                                  ? 'bg-green-100 text-green-800'
                                  : 'bg-red-100 text-red-800'
                              }`}>
                                {user.is_active ? 'Active' : 'Suspended'}
                              </span>
                            </td>
                            <td className="px-4 py-2 whitespace-nowrap text-sm font-medium space-x-2">
                              <button
                                onClick={() => {
                                  fetchRoles();
                                  setEditingUser(user);
                                  setEditForm({
                                    email: user.email,
                                    full_name: user.full_name,
                                    role_id: user.role_id
                                  });
                                }}
                                className="text-blue-600 hover:text-blue-900"
                              >
                                Edit
                              </button>
                              {user.is_active ? (
                                <button
                                  onClick={() => handleSuspendUser(user.id)}
                                  className="text-red-600 hover:text-red-900"
                                >
                                  Suspend
                                </button>
                              ) : (
                                <button
                                  onClick={() => handleActivateUser(user.id)}
                                  className="text-green-600 hover:text-green-900"
                                >
                                  Activate
                                </button>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* User Profiles Tab */}
        {activeTab === 'profiles' && (
          <div className="space-y-4">
            {/* Create Button and Search Section */}
            <div className="bg-white rounded-lg shadow p-4">
              <h2 className="text-xl font-bold text-gray-900 mb-4">User Profiles</h2>

              {/* Search Filter - Single Unified Search Box */}
              <div className="flex gap-2">
                <div className="flex-1">
                  <input
                    type="text"
                    value={searchProfileQuery}
                    onChange={(e) => {
                      setSearchProfileQuery(e.target.value);
                      if (e.target.value === '') {
                        setFilteredProfiles(profiles);
                      }
                    }}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        handleSearchProfiles(e);
                      }
                    }}
                    placeholder="Search by profile name or description"
                    className="w-full px-3 py-1.5 border border-gray-300 rounded-lg shadow-sm text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <button
                  onClick={handleSearchProfiles}
                  className="px-4 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium text-sm"
                >
                  Search
                </button>
                <button
                  onClick={() => setShowCreateProfileModal(true)}
                  className="px-4 py-1.5 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-medium text-sm"
                >
                  + Add New Profile
                </button>
              </div>
            </div>

            {/* View Profiles Table */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-4 py-3">
                <h2 className="text-lg font-bold text-gray-900 mb-4">All Profiles</h2>
                {loading ? (
                  <p className="text-center text-gray-500 py-4 text-sm">Loading...</p>
                ) : filteredProfiles.length === 0 ? (
                  <p className="text-center text-gray-500 py-4 text-sm">No profiles found</p>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role Name</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role Code</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {filteredProfiles.map((profile) => (
                          <tr key={profile.id} className="hover:bg-gray-50">
                            <td className="px-4 py-2 whitespace-nowrap text-sm font-medium text-gray-900">{profile.role_name}</td>
                            <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-600">{profile.role_code}</td>
                            <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-600">{profile.description}</td>
                            <td className="px-4 py-2 whitespace-nowrap text-sm font-medium space-x-2">
                              <button
                                onClick={() => {
                                  setEditingProfile(profile);
                                  setEditProfileForm({
                                    role_name: profile.role_name,
                                    role_code: profile.role_code,
                                    description: profile.description,
                                    dashboard_route: profile.dashboard_route
                                  });
                                }}
                                className="text-blue-600 hover:text-blue-900"
                              >
                                Edit
                              </button>
                              <button
                                onClick={() => handleDeleteProfile(profile.id)}
                                className="text-red-600 hover:text-red-900"
                              >
                                Delete
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Create User Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-lg p-6 max-w-md w-full">
              <h3 className="text-xl font-bold text-gray-900 mb-6">Add New User</h3>
              <form onSubmit={handleCreateUser} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Username</label>
                  <input
                    type="text"
                    required
                    value={createForm.username}
                    onChange={(e) => setCreateForm({...createForm, username: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Enter username"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                  <input
                    type="email"
                    required
                    value={createForm.email}
                    onChange={(e) => setCreateForm({...createForm, email: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Enter email"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Full Name</label>
                  <input
                    type="text"
                    required
                    value={createForm.full_name}
                    onChange={(e) => setCreateForm({...createForm, full_name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Enter full name"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
                  <input
                    type="password"
                    required
                    value={createForm.password}
                    onChange={(e) => setCreateForm({...createForm, password: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Enter password"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">User Profile</label>
                  <select
                    required
                    value={createForm.role_id}
                    onChange={(e) => setCreateForm({...createForm, role_id: parseInt(e.target.value)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Select a user profile</option>
                    {profiles.map((profile) => (
                      <option key={profile.id} value={profile.id}>
                        {profile.role_name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="flex gap-3">
                  <button
                    type="submit"
                    disabled={loading}
                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition font-medium"
                  >
                    {loading ? 'Creating...' : 'Create User'}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowCreateModal(false);
                      setCreateForm({username: '', password: '', email: '', full_name: '', profile_id: ''});
                    }}
                    className="flex-1 px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition font-medium"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Edit User Modal */}
        {editingUser && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-lg p-6 max-w-md w-full">
              <h3 className="text-xl font-bold text-gray-900 mb-4">Edit User</h3>
              <form onSubmit={handleUpdateUser} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                  <input
                    type="email"
                    value={editForm.email}
                    onChange={(e) => setEditForm({...editForm, email: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Full Name</label>
                  <input
                    type="text"
                    value={editForm.full_name}
                    onChange={(e) => setEditForm({...editForm, full_name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Role</label>
                  <select
                    value={editForm.role_id}
                    onChange={(e) => setEditForm({...editForm, role_id: parseInt(e.target.value)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  >
                    {roles.map((role) => (
                      <option key={role.id} value={role.id}>
                        {role.role_name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="flex space-x-4">
                  <button
                    type="submit"
                    disabled={loading}
                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition"
                  >
                    {loading ? 'Saving...' : 'Save Changes'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setEditingUser(null)}
                    className="flex-1 px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Create Profile Modal */}
        {showCreateProfileModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-lg p-6 max-w-md w-full">
              <h3 className="text-xl font-bold text-gray-900 mb-6">Add New Profile</h3>
              <form onSubmit={handleCreateProfile} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Role Name</label>
                  <input
                    type="text"
                    required
                    value={profileForm.role_name}
                    onChange={(e) => setProfileForm({...profileForm, role_name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Enter role name"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Role Code</label>
                  <input
                    type="text"
                    required
                    value={profileForm.role_code}
                    onChange={(e) => setProfileForm({...profileForm, role_code: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Enter role code (e.g., ADMIN)"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                  <textarea
                    required
                    value={profileForm.description}
                    onChange={(e) => setProfileForm({...profileForm, description: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Enter description"
                    rows="3"
                  />
                </div>
                <div className="flex gap-3">
                  <button
                    type="submit"
                    disabled={loading}
                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition font-medium"
                  >
                    {loading ? 'Creating...' : 'Create Profile'}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowCreateProfileModal(false);
                      setProfileForm({ role_name: '', role_code: '', description: '' });
                    }}
                    className="flex-1 px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition font-medium"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Edit Profile Modal */}
        {editingProfile && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-lg p-6 max-w-md w-full">
              <h3 className="text-xl font-bold text-gray-900 mb-6">Edit Profile</h3>
              <form onSubmit={handleUpdateProfile} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Role Name</label>
                  <input
                    type="text"
                    required
                    value={editProfileForm.role_name}
                    onChange={(e) => setEditProfileForm({...editProfileForm, role_name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Role Code</label>
                  <input
                    type="text"
                    required
                    value={editProfileForm.role_code}
                    onChange={(e) => setEditProfileForm({...editProfileForm, role_code: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                  <textarea
                    required
                    value={editProfileForm.description}
                    onChange={(e) => setEditProfileForm({...editProfileForm, description: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    rows="3"
                  />
                </div>
                {/* Dashboard Route is hidden but maintained in state for API */}
                <input type="hidden" value={editProfileForm.dashboard_route} />
                <div className="flex gap-3">
                  <button
                    type="submit"
                    disabled={loading}
                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition font-medium"
                  >
                    {loading ? 'Saving...' : 'Save Changes'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setEditingProfile(null)}
                    className="flex-1 px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition font-medium"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
