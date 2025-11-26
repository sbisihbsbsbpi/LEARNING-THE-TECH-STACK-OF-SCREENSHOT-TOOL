/**
 * 🍞 Toast Notification Component
 *
 * Individual toast notification with auto-dismiss, manual dismiss, and animations.
 *
 * @module components/shared/Toast
 * @author AI Assistant
 * @date 2025-11-14
 *
 * @example
 * ```tsx
 * <Toast
 *   notification={{
 *     id: "1",
 *     type: "success",
 *     title: "Success",
 *     message: "Screenshot captured!",
 *     duration: 5000,
 *     dismissible: true,
 *     timestamp: new Date()
 *   }}
 *   onDismiss={(id) => removeNotification(id)}
 * />
 * ```
 */

import React, { useEffect, useState } from "react";
import { ToastNotification } from "../../types/notification";

interface ToastProps {
  notification: ToastNotification;
  onDismiss: (id: string) => void;
}

/**
 * Get icon for notification type
 */
const getIcon = (type: string, customIcon?: string): string => {
  if (customIcon) return customIcon;

  switch (type) {
    case "success":
      return "✅";
    case "error":
      return "❌";
    case "warning":
      return "⚠️";
    case "info":
    default:
      return "ℹ️";
  }
};

/**
 * Toast component
 */
export const Toast: React.FC<ToastProps> = ({ notification, onDismiss }) => {
  const [isExiting, setIsExiting] = useState(false);
  const [progress, setProgress] = useState(100);

  console.log(
    `🍞 Toast rendered: ${notification.id} - ${notification.type} - ${notification.title}`
  );

  // Auto-dismiss logic
  useEffect(() => {
    if (!notification.duration || notification.duration === 0) {
      console.log(
        `🍞 Toast ${notification.id}: No auto-dismiss (duration = 0)`
      );
      return;
    }

    console.log(
      `🍞 Toast ${notification.id}: Auto-dismiss in ${notification.duration}ms`
    );

    // Progress bar animation
    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        const decrement = (100 / notification.duration!) * 50; // Update every 50ms
        return Math.max(0, prev - decrement);
      });
    }, 50);

    // Auto-dismiss timer
    const timer = setTimeout(() => {
      console.log(`🍞 Toast ${notification.id}: Auto-dismissing now`);
      handleDismiss();
    }, notification.duration);

    return () => {
      clearTimeout(timer);
      clearInterval(progressInterval);
      console.log(`🍞 Toast ${notification.id}: Cleanup timers`);
    };
  }, [notification.duration, notification.id]);

  const handleDismiss = () => {
    console.log(`🍞 Toast ${notification.id}: Starting exit animation`);
    setIsExiting(true);

    // Wait for animation to complete before removing
    setTimeout(() => {
      console.log(`🍞 Toast ${notification.id}: Calling onDismiss`);
      onDismiss(notification.id);
    }, 300); // Match CSS animation duration
  };

  const icon = getIcon(notification.type, notification.icon);

  return (
    <div
      className={`toast toast-${notification.type} ${
        isExiting ? "toast-exit" : "toast-enter"
      }`}
      role="alert"
      aria-live="polite"
      aria-atomic="true"
      style={{
        position: "fixed",
        top: notification.position
          ? `${notification.position.top}px`
          : undefined,
        left: notification.position
          ? `${notification.position.left}px`
          : undefined,
        zIndex: 999999,
      }}
    >
      <div className="toast-content">
        <div className="toast-icon" aria-hidden="true">
          {icon}
        </div>
        <div className="toast-body">
          <div className="toast-title">{notification.title}</div>
          <div className="toast-message">{notification.message}</div>
        </div>
        {notification.dismissible !== false && (
          <button
            className="toast-close"
            onClick={handleDismiss}
            aria-label="Dismiss notification"
            title="Dismiss"
          >
            ✕
          </button>
        )}
      </div>
      {notification.duration && notification.duration > 0 && (
        <div className="toast-progress">
          <div
            className="toast-progress-bar"
            style={{ width: `${progress}%` }}
            aria-hidden="true"
          />
        </div>
      )}
    </div>
  );
};

export default Toast;
