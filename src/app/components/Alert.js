'use client';

export default function Alert({ type = 'success', message }) {
  if (!message) return null;

  const alertStyles = {
    success: {
      bg: 'bg-green-50',
      border: 'border-green-400',
      text: 'text-green-700'
    },
    error: {
      bg: 'bg-red-50',
      border: 'border-red-400',
      text: 'text-red-700'
    },
    warning: {
      bg: 'bg-yellow-50',
      border: 'border-yellow-400',
      text: 'text-yellow-700'
    },
    info: {
      bg: 'bg-blue-50',
      border: 'border-blue-400',
      text: 'text-blue-700'
    }
  };

  const style = alertStyles[type] || alertStyles.success;

  return (
    <div className={`mb-4 p-4 ${style.bg} border-l-4 ${style.border} rounded-lg`}>
      <p className={style.text}>{message}</p>
    </div>
  );
}
