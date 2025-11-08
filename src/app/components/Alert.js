"use client";

import { useEffect, useState } from 'react';

export default function Alert({
  type = 'success',
  message,
  onClose,
  fixed = false,
  autoHide = true,
  timeout = 5000
}) {
  const [visible, setVisible] = useState(Boolean(message));

  useEffect(() => {
    setVisible(Boolean(message));
  }, [message]);

  useEffect(() => {
    if (!visible) return;
    if (!autoHide) return;
    const t = setTimeout(() => {
      setVisible(false);
      if (typeof onClose === 'function') onClose();
    }, timeout);
    return () => clearTimeout(t);
  }, [visible, autoHide, timeout, onClose]);

  if (!message || !visible) return null;

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

  const containerClass = fixed
    ? 'fixed top-4 right-4 z-50 w-full max-w-sm'
    : 'mb-4';

  return (
    <div className={`${containerClass}`}>
      <div className={`p-4 ${style.bg} border-l-4 ${style.border} rounded-lg shadow-md flex items-start justify-between`}> 
        <p className={`${style.text} mr-4 flex-1`}>{message}</p>
        <button
          aria-label="Close alert"
          onClick={() => {
            setVisible(false);
            if (typeof onClose === 'function') onClose();
          }}
          className="text-gray-500 hover:text-gray-700 ml-2"
        >
          ✕
        </button>
      </div>
    </div>
  );
}
