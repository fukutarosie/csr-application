# Reusable Card Components - Implementation Guide

## Overview

Created two reusable components to promote code reusability and consistency across PIN and CSR dashboards:

1. **`RequestCard.js`** - Individual card component for displaying request/shortlist items
2. **`RequestCardGrid.js`** - Grid container component with empty state handling

---

## Component Files Created

### 1. `/src/app/components/RequestCard.js`

A flexible, reusable card component that handles:
- Request images with fallback placeholders
- Status badges
- Service type, region, and date information
- Custom theme colors (blue for PIN, purple for CSR)
- Custom extra information slots
- Custom action buttons

**Props:**
- `request` (Object) - The request/shortlist data
- `onClick` (Function) - Click handler
- `theme` (String) - 'blue' or 'purple' (default: 'blue')
- `extraInfo` (ReactNode) - Optional extra content to display
- `actionButton` (ReactNode) - Optional custom button/action

### 2. `/src/app/components/RequestCardGrid.js`

A responsive grid container that handles:
- Responsive layout (1/2/3 columns)
- Empty state with custom message and icon
- Optional empty state action button

**Props:**
- `children` (ReactNode) - RequestCard components
- `emptyMessage` (String) - Message when no items (default: "No items found")
- `emptyIcon` (String) - Emoji for empty state (default: "📝")
- `emptyAction` (ReactNode) - Optional action button for empty state

---

## Usage Examples

### Example 1: PIN Landing Page (`/src/app/pin/page.js`)

```javascript
// 1. Import the components
import RequestCard from '../components/RequestCard';
import RequestCardGrid from '../components/RequestCardGrid';

// 2. In your JSX, replace the old grid code with:
<RequestCardGrid
  emptyMessage="No requests yet"
  emptyIcon="📝"
  emptyAction={
    <button
      onClick={() => router.push('/pin/request/new')}
      className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors"
    >
      Create Your First Request
    </button>
  }
>
  {recentRequests.map((request) => (
    <RequestCard
      key={request.id}
      request={request}
      onClick={() => router.push(`/pin/request/${request.id}`)}
      theme="blue"
      extraInfo={
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center text-gray-600">
            <span className="mr-1">👁️</span>
            <span>{request.view_count || 0} views</span>
          </div>
          <div className="flex items-center text-gray-600">
            <span className="mr-1">⭐</span>
            <span>{request.shortlist_count || 0} saved</span>
          </div>
        </div>
      }
    />
  ))}
</RequestCardGrid>
```

### Example 2: CSR Landing Page (`/src/app/csr/page.js`)

```javascript
// 1. Import the components
import RequestCard from '../components/RequestCard';
import RequestCardGrid from '../components/RequestCardGrid';

// 2. In your JSX, replace the old grid code with:
<RequestCardGrid
  emptyMessage="No requests in your shortlist yet"
  emptyIcon="📋"
  emptyAction={
    <button
      onClick={() => router.push('/csr/browse')}
      className="mt-4 px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700"
    >
      Browse Requests
    </button>
  }
>
  {recentShortlist.map((item) => (
    <RequestCard
      key={item.id}
      request={item.requests} // Note: nested object for CSR shortlist
      onClick={() => router.push('/csr/shortlist')}
      theme="purple"
      extraInfo={
        <div className="flex items-center text-sm">
          <svg className="w-4 h-4 text-blue-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <span className="text-gray-700 text-xs">Shortlisted: {new Date(item.shortlisted_at).toLocaleDateString()}</span>
        </div>
      }
    />
  ))}
</RequestCardGrid>
```

### Example 3: PIN Dashboard (`/src/app/pin/dashboard/page.js`)

```javascript
// 1. Import the components
import RequestCard from '../../components/RequestCard';
import RequestCardGrid from '../../components/RequestCardGrid';

// 2. In your JSX:
<RequestCardGrid
  emptyMessage="No requests match your search criteria"
  emptyIcon="🔍"
  emptyAction={
    <button 
      onClick={clearFilters}
      className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
    >
      Clear Filters
    </button>
  }
>
  {filteredRequests.map((req) => (
    <RequestCard
      key={req.id}
      request={req}
      onClick={() => router.push(`/pin/request/${req.id}`)}
      theme="blue"
    />
  ))}
</RequestCardGrid>
```

### Example 4: CSR Browse Page (`/src/app/csr/browse/page.js`)

```javascript
// 1. Import the components
import RequestCard from '../../components/RequestCard';
import RequestCardGrid from '../../components/RequestCardGrid';

// 2. In your JSX:
<RequestCardGrid
  emptyMessage="No opportunities found"
  emptyIcon="🔍"
  emptyAction={
    <button
      onClick={clearFilters}
      className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
    >
      Clear Filters
    </button>
  }
>
  {filteredRequests.map((request) => {
    const isShortlisted = shortlistedIds.includes(request.id);
    return (
      <RequestCard
        key={request.id}
        request={request}
        onClick={() => router.push(`/csr/browse/${request.id}`)}
        theme="purple"
        actionButton={
          <div className="flex items-center justify-between">
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleToggleShortlist(request.id);
              }}
              className="text-2xl transition-transform hover:scale-110"
            >
              {isShortlisted ? '❤️' : '🤍'}
            </button>
            <button className="flex-1 ml-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700">
              View Details
            </button>
          </div>
        }
      />
    );
  })}
</RequestCardGrid>
```

---

## Benefits of Component Approach

### 1. **Code Reusability**
- Single card design used across 4+ pages
- Consistent visual appearance
- DRY (Don't Repeat Yourself) principle

### 2. **Easy Maintenance**
- Update card design in one place
- Changes automatically propagate to all pages
- Easier to fix bugs and add features

### 3. **Flexibility**
- Props system allows customization per use case
- Theme support (blue/purple)
- Custom extra info and actions
- Extensible for future needs

### 4. **Consistency**
- Same look and feel everywhere
- Standardized spacing, colors, and layout
- Professional appearance

### 5. **Testability**
- Components can be unit tested separately
- Easier to isolate bugs
- Better code quality

---

## Component Features

### RequestCard Features:
✅ Responsive image with fallback placeholder  
✅ Status badge overlay  
✅ Title with line clamping (2 lines max)  
✅ Description with line clamping (2 lines max)  
✅ Service type with icon  
✅ Region/location with icon  
✅ Requested by date with icon  
✅ Custom extra info slot  
✅ Custom action button slot  
✅ Theme support (blue/purple)  
✅ Hover effects and transitions  
✅ Click handler support  

### RequestCardGrid Features:
✅ Responsive 1/2/3 column layout  
✅ Empty state handling  
✅ Custom empty message and icon  
✅ Optional empty state action  
✅ Automatic grid rendering  

---

## Migration Steps

### Step 1: Import Components
Add these imports to the top of your page file:
```javascript
import RequestCard from '../components/RequestCard';
import RequestCardGrid from '../components/RequestCardGrid';
```

### Step 2: Remove Old Code
Delete the old conditional rendering and grid code:
```javascript
// DELETE THIS:
{items.length === 0 ? (
  <div className="text-center py-8">...</div>
) : (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    {items.map((item) => (
      <div className="bg-white rounded-lg shadow-md...">
        ...lots of code...
      </div>
    ))}
  </div>
)}
```

### Step 3: Add New Component Usage
Replace with component-based code:
```javascript
<RequestCardGrid emptyMessage="..." emptyIcon="..." emptyAction={...}>
  {items.map((item) => (
    <RequestCard key={item.id} request={item} theme="blue" {...otherProps} />
  ))}
</RequestCardGrid>
```

---

## Files to Update

1. ✅ **`src/app/components/RequestCard.js`** - Created
2. ✅ **`src/app/components/RequestCardGrid.js`** - Created
3. 🔄 **`src/app/pin/page.js`** - Replace lines ~215-310 with component usage
4. 🔄 **`src/app/pin/dashboard/page.js`** - Replace card grid section with component usage
5. 🔄 **`src/app/csr/page.js`** - Replace lines ~125-180 with component usage
6. 🔄 **`src/app/csr/browse/page.js`** - Replace card grid section with component usage

---

## Testing Checklist

After migrating to components:

- [ ] PIN landing page displays cards correctly
- [ ] PIN dashboard displays cards correctly
- [ ] CSR landing page displays cards correctly
- [ ] CSR browse page displays cards correctly
- [ ] Empty states show correct messages
- [ ] Click handlers work properly
- [ ] Hover effects still work
- [ ] Images load correctly
- [ ] Status badges display correctly
- [ ] Theme colors are correct (blue/purple)
- [ ] Responsive layout works (mobile/tablet/desktop)
- [ ] Extra info displays correctly (views, shortlist counts, dates)
- [ ] Custom action buttons work

---

## Future Enhancements

With these reusable components, you can easily add:
- [ ] Loading skeleton states
- [ ] Favorite/like animations
- [ ] Card flip effects
- [ ] More theme colors
- [ ] Different card sizes (small/medium/large)
- [ ] Card actions menu (edit/delete/share)
- [ ] Drag and drop reordering
- [ ] Card selection (checkboxes)

---

## Conclusion

The `RequestCard` and `RequestCardGrid` components provide a **solid foundation for code reusability** across your application. They follow React best practices and make your codebase more maintainable and scalable.

**Next Steps:**
1. Review the component files created
2. Follow the usage examples to update each page
3. Test thoroughly
4. Enjoy cleaner, more maintainable code! 🎉
