import React from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface InputFieldProps {
  id: string;
  label: string;
  type?: string;
  placeholder?: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  error?: string | undefined;
  required?: boolean;
  className?: string;
  disabled?: boolean;
}

const InputField: React.FC<InputFieldProps> = ({
  id,
  label,
  type = "text",
  placeholder,
  value,
  onChange,
  error,
  required = false,
  className = "",
  disabled = false,
}) => (
  <div className={`mb-4 ${className}`}>
    <Label
      htmlFor={id}
      className="block text-sm font-medium text-gray-700 mb-2"
    >
      {label}
      {required && <span className="text-red-500 ml-1">*</span>}
    </Label>
    <Input
      id={id}
      type={type}
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      required={required}
      className={`
          w-full px-3 py-2 border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors
          ${error ? "border-red-500 bg-red-50" : "border-gray-300 bg-white hover:border-gray-400"}
        `}
      disabled={disabled}
    />
    {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
  </div>
);

export { InputField };
