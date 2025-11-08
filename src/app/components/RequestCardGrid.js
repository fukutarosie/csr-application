/**
 * RequestCardGrid Component
 * 
 * A responsive grid container for displaying multiple RequestCard components.
 * Automatically adjusts columns based on screen size:
 * - Mobile: 1 column
 * - Tablet: 2 columns
 * - Desktop: 3 columns
 * 
 * @param {ReactNode} children - RequestCard components to display
 * @param {string} emptyMessage - Message to show when no items
 * @param {string} emptyIcon - Emoji/icon for empty state
 * @param {ReactNode} emptyAction - Custom action button for empty state
 */

export default function RequestCardGrid({ 
  children, 
  emptyMessage = 'No items found',
  emptyIcon = '📝',
  emptyAction = null 
}) {
  const hasItems = children && (Array.isArray(children) ? children.length > 0 : true);

  return (
    <>
      {!hasItems ? (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">{emptyIcon}</div>
          <p className="text-gray-600 mb-4">{emptyMessage}</p>
          {emptyAction}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {children}
        </div>
      )}
    </>
  );
}
