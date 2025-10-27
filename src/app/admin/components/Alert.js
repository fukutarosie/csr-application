'use client';

export default function Alert({ type = 'success', message }) {
  if (!message) return null;

  const styles = {
    success: 'bg-green-50 border-l-4 border-green-400',
    error: 'bg-red-50 border-l-4 border-red-400',
    warning: 'bg-yellow-50 border-l-4 border-yellow-400',
    info: 'bg-blue-50 border-l-4 border-blue-400'
  };

  const textStyles = {
    success: 'text-green-700',
    error: 'text-red-700',
    warning: 'text-yellow-700',
    info: 'text-blue-700'
  };

  return (
    <div className={`mb-4 p-4 rounded-lg ${styles[type]}`}>
      <p className={textStyles[type]}>{message}</p>
    </div>
  );
}
