/**
 * RequestCard Component
 * 
 * A reusable card component for displaying PIN requests and CSR shortlisted items
 * with a consistent visual design across the application.
 * 
 * @param {Object} request - The request/shortlist item data
 * @param {Function} onClick - Click handler for the card
 * @param {string} theme - Color theme: 'blue' (PIN) or 'purple' (CSR)
 * @param {Object} extraInfo - Optional extra information to display
 * @param {ReactNode} actionButton - Optional custom action button/content
 */

export default function RequestCard({ 
  request, 
  onClick, 
  theme = 'blue',
  extraInfo = null,
  actionButton = null,
  analytics = null,  // 🆕 US-27 & US-28: Analytics data
  badge = null  // 🆕 Custom badge to display (e.g., shortlist indicator)
}) {
  const themeColors = {
    blue: {
      gradient: 'from-blue-100 to-blue-200',
      icon: 'text-blue-400',
      serviceType: 'text-blue-500',
      border: 'hover:border-blue-400',
      title: 'hover:text-blue-600',
      button: 'text-blue-600 hover:text-blue-800 hover:bg-blue-50'
    },
    purple: {
      gradient: 'from-purple-100 to-purple-200',
      icon: 'text-purple-400',
      serviceType: 'text-purple-500',
      border: 'hover:border-purple-400',
      title: 'hover:text-purple-600',
      button: 'text-purple-600 hover:text-purple-800 hover:bg-purple-50'
    }
  };

  const colors = themeColors[theme] || themeColors.blue;

  const displayStatus = request.assignment_status || request.status;

  const getStatusBadge = (status) => {
    const statusColors = {
      'ACTIVE': 'bg-green-100 text-green-800',
      'SUSPENDED': 'bg-yellow-100 text-yellow-800',
      'FULFILLED': 'bg-blue-100 text-blue-800',
      'CANCELLED': 'bg-red-100 text-red-800',
      'SHORTLISTED': 'bg-purple-100 text-purple-800',
      'IN_PROGRESS': 'bg-blue-100 text-blue-800',
      'COMPLETED': 'bg-green-100 text-green-800',
      'DECLINED': 'bg-red-100 text-red-800'
    };
    return statusColors[status] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div 
      onClick={onClick}
      className={`bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow duration-300 overflow-hidden cursor-pointer border border-gray-200 ${colors.border} relative`}
    >
      {/* Custom Badge (e.g., Shortlisted indicator) */}
      {badge}
      
      {/* Image */}
      <div className="relative h-48 bg-gray-200">
        {request.image_url ? (
          <img 
            src={`http://localhost:5000${request.image_url}`}
            alt={request.title}
            className="w-full h-full object-cover"
            onError={(e) => {
              e.target.style.display = 'none';
              e.target.nextElementSibling.style.display = 'flex';
            }}
          />
        ) : null}
        {/* Placeholder (shown if no image or image fails to load) */}
        <div 
          className={`w-full h-full flex items-center justify-center bg-gradient-to-br ${colors.gradient}`}
          style={{ display: request.image_url ? 'none' : 'flex' }}
        >
          <svg className={`w-20 h-20 ${colors.icon}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>
        
        {/* Status Badge Overlay */}
      {displayStatus && (
          <div className="absolute top-3 right-3">
          <span className={`px-3 py-1 rounded-full text-xs font-bold shadow-lg ${getStatusBadge(displayStatus)}`}>
            {displayStatus.replace('_', ' ')}
            </span>
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-5">
        {/* Title */}
        <h3 className={`text-lg font-bold text-gray-800 mb-2 line-clamp-2 ${colors.title} transition`}>
          {request.title}
        </h3>

        {/* Description */}
        {request.description && (
          <p className="text-gray-600 text-sm mb-4 line-clamp-2">
            {request.description}
          </p>
        )}

        {/* Details */}
        <div className="space-y-2 mb-4">
          {/* Service Type */}
          {request.service_type && (
            <div className="flex items-center text-sm">
              <svg className={`w-4 h-4 ${colors.serviceType} mr-2`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              <span className="text-gray-700 font-medium">{request.service_type}</span>
            </div>
          )}

          {/* Region */}
          {request.region && (
            <div className="flex items-center text-sm">
              <svg className="w-4 h-4 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <span className="text-gray-700">{request.region}</span>
            </div>
          )}

          {/* Requested By Date */}
          {request.requested_by_date && (
            <div className="flex items-center text-sm">
              <svg className="w-4 h-4 text-red-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <span className="text-gray-700">{new Date(request.requested_by_date).toLocaleDateString()}</span>
            </div>
          )}

          {/* Extra Info (custom content passed from parent) */}
          {extraInfo}

          {/* Assignment info fallback */}
          {!extraInfo && request.active_assignment && request.active_assignment.csr_user && (
            <div className="flex items-center text-sm text-purple-700 font-medium bg-purple-50 border border-purple-200 rounded-lg px-3 py-2">
              <span className="mr-2">👤</span>
              <span>
                {request.assignment_status === 'IN_PROGRESS'
                  ? `In progress by ${request.active_assignment.csr_user.full_name}`
                  : `Completed by ${request.active_assignment.csr_user.full_name}`}
              </span>
            </div>
          )}
        </div>

        {/* 🆕 US-27 & US-28: Analytics Section */}
        {analytics && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="flex gap-6 justify-center">
              <div className="flex items-center gap-2">
                <span className="text-2xl">👁️</span>
                <div>
                  <p className="text-xs text-gray-500 font-medium">Views</p>
                  <p className="text-lg font-bold text-blue-600">
                    {analytics.view_count || 0}
                  </p>
                </div>
              </div>
              
              <div className="flex items-center gap-2">
                <span className="text-2xl">⭐</span>
                <div>
                  <p className="text-xs text-gray-500 font-medium">Shortlisted</p>
                  <p className="text-lg font-bold text-purple-600">
                    {analytics.shortlist_count || 0}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Footer Button or Custom Action */}
        <div className="pt-3 border-t border-gray-200">
          {actionButton ? (
            actionButton
          ) : (
            <button className={`w-full text-center font-semibold text-sm py-2 rounded transition ${colors.button}`}>
              View Details →
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
