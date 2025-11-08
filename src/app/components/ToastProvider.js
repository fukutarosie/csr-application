"use client";

import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';

const ToastContext = createContext(null);

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const push = useCallback(({ type = 'success', message = '', timeout = 4500 }) => {
    const id = Date.now().toString(36) + Math.random().toString(36).slice(2, 9);
    const toast = { id, type, message, timeout };
    setToasts((s) => [...s, toast]);
    return id;
  }, []);

  const remove = useCallback((id) => {
    setToasts((s) => s.filter(t => t.id !== id));
  }, []);

  // automatically remove toasts when their timeout expires
  useEffect(() => {
    const timers = toasts.map((t) => {
      if (!t.timeout) return null;
      return setTimeout(() => remove(t.id), t.timeout);
    }).filter(Boolean);
    return () => timers.forEach((t) => clearTimeout(t));
  }, [toasts, remove]);

  const api = {
    success: (message, opts = {}) => push({ type: 'success', message, timeout: opts.timeout ?? 4000 }),
    error: (message, opts = {}) => push({ type: 'error', message, timeout: opts.timeout ?? 6000 }),
    info: (message, opts = {}) => push({ type: 'info', message, timeout: opts.timeout ?? 4500 }),
    warning: (message, opts = {}) => push({ type: 'warning', message, timeout: opts.timeout ?? 4500 }),
    remove
  };

  return (
    <ToastContext.Provider value={api}>
      {children}

      {/* Toast container */}
      <div aria-live="polite" className="fixed top-4 right-4 z-50 flex flex-col gap-3 max-w-sm w-full">
        {toasts.map((t) => (
          <div key={t.id} className={`p-3 rounded shadow-md border-l-4 ${t.type === 'success' ? 'bg-green-50 border-green-400 text-green-700' : t.type === 'error' ? 'bg-red-50 border-red-400 text-red-700' : 'bg-blue-50 border-blue-400 text-blue-700'}`}>
            <div className="flex items-start justify-between">
              <div className="mr-4 break-words">{t.message}</div>
              <button aria-label="Dismiss" onClick={() => remove(t.id)} className="text-gray-500 hover:text-gray-700">✕</button>
            </div>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export const useToast = () => {
  const ctx = useContext(ToastContext);
  if (!ctx) {
    // provide a safe fallback so components can call toast.* even if provider missing
    return {
      success: () => {},
      error: () => {},
      info: () => {},
      warning: () => {},
      remove: () => {}
    };
  }
  return ctx;
};
