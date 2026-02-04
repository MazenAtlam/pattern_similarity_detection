// hooks/use-toast.js
import { useState, useCallback } from "react";

const useToast = () => {
  const [toasts, setToasts] = useState([]);

  const toast = useCallback(({ title, description, variant = "default" }) => {
    // Create a unique ID for the toast
    const id = Date.now();

    // Map variant to Bootstrap alert classes
    const variantClasses = {
      default: "alert-primary",
      destructive: "alert-danger",
    };

    const newToast = {
      id,
      title,
      description,
      variant: variantClasses[variant] || variantClasses.default,
    };

    setToasts((prev) => [...prev, newToast]);

    // Auto remove toast after 5 seconds
    setTimeout(() => {
      setToasts((prev) => prev.filter((toast) => toast.id !== id));
    }, 5000);
  }, []);

  return { toast, toasts };
};

export { useToast };
