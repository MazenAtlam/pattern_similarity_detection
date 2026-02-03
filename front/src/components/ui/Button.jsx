// components/ui/Button.js
import React from "react";

const Button = ({
                    children,
                    variant = "default",
                    size = "md",
                    className = "",
                    disabled = false,
                    onClick,
                    type = "button",
                    ...props
                }) => {
    // Map variants to Bootstrap classes
    const variantClasses = {
        default: "btn-primary",
        primary: "btn-primary",
        secondary: "btn-secondary",
        success: "btn-success",
        danger: "btn-danger",
        warning: "btn-warning",
        info: "btn-info",
        light: "btn-light",
        dark: "btn-dark",
        link: "btn-link",
        outline: "btn-outline-primary",
        ghost: "btn-link text-dark",
        destructive: "btn-danger",
    };

    // Map sizes to Bootstrap classes
    const sizeClasses = {
        sm: "btn-sm",
        md: "",
        lg: "btn-lg",
        icon: "btn-sm p-2",
    };

    const baseClass = "btn";
    const variantClass = variantClasses[variant] || variantClasses.default;
    const sizeClass = sizeClasses[size] || "";

    return (
        <button
            type={type}
            className={`${baseClass} ${variantClass} ${sizeClass} ${className}`}
            disabled={disabled}
            onClick={onClick}
            {...props}
        >
            {children}
        </button>
    );
};

export default Button;