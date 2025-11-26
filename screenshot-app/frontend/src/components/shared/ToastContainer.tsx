/**
 * 🍞 Toast Container Component
 *
 * Container for managing and displaying multiple toast notifications.
 * Handles stacking, positioning, and z-index management.
 *
 * @module components/shared/ToastContainer
 * @author AI Assistant
 * @date 2025-11-14
 *
 * @example
 * ```tsx
 * <ToastContainer
 *   notifications={notifications}
 *   onDismiss={removeNotification}
 *   position="top-right"
 *   maxVisible={5}
 * />
 * ```
 */

import React from "react";
import { ToastNotification } from "../../types/notification";
import Toast from "./Toast";

interface ToastContainerProps {
  notifications: ToastNotification[];
  onDismiss: (id: string) => void;
  position?: "top-right" | "top-left" | "bottom-right" | "bottom-left";
  maxVisible?: number;
}

/**
 * Toast container component
 */
export const ToastContainer: React.FC<ToastContainerProps> = ({
  notifications,
  onDismiss,
  position = "top-right",
  maxVisible = 5,
}) => {
  console.log(
    `🍞 ToastContainer: Rendering ${notifications.length} notifications (max visible: ${maxVisible})`
  );

  // Limit visible notifications
  const visibleNotifications = notifications.slice(0, maxVisible);

  if (visibleNotifications.length < notifications.length) {
    console.log(
      `🍞 ToastContainer: Hiding ${
        notifications.length - visibleNotifications.length
      } notifications (exceeds max)`
    );
  }

  return (
    <div
      aria-live="polite"
      aria-atomic="false"
      role="region"
      aria-label="Notifications"
      style={{ position: "relative" }}
    >
      {visibleNotifications.map((notification) => (
        <Toast
          key={notification.id}
          notification={notification}
          onDismiss={onDismiss}
        />
      ))}
    </div>
  );
};

export default ToastContainer;
