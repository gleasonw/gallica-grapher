import React from "react";

interface TextInputProps {
  placeholder: string;
  numValue?: number;
  isNumber?: boolean;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onKeyPress?: (e: React.KeyboardEvent<HTMLInputElement>) => void;
}

export const TextInput: React.FC<TextInputProps> = ({
  placeholder,
  value,
  onChange,
  onKeyPress,
}) => {
  return (
    <input
      className="text-2xl border-4 rounded-md p-5"
      placeholder={placeholder}
      value={value || ""}
      onChange={onChange}
      onKeyPress={onKeyPress}
    />
  )
};
