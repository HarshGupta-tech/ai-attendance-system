import React, { forwardRef } from 'react';

const Input = forwardRef(({
  label,
  id,
  type = 'text',
  error,
  helperText,
  iconLeft: IconLeft,
  className = '',
  required = false,
  options = [], // for select type
  rows = 4, // for textarea type
  ...props
}, ref) => {
  const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;
  
  const baseInputClasses = `block w-full rounded-md shadow-sm sm:text-sm transition-colors duration-200
    ${error 
      ? 'border-red-300 text-red-900 focus:ring-red-500 focus:border-red-500 placeholder-red-300' 
      : 'border-gray-300 focus:ring-indigo-500 focus:border-indigo-500'
    }
    ${IconLeft ? 'pl-10' : 'pl-3'}
    ${props.disabled ? 'bg-gray-100 cursor-not-allowed text-gray-500' : 'bg-white'}
  `;

  const renderInput = () => {
    if (type === 'select') {
      return (
        <select
          id={inputId}
          ref={ref}
          className={`${baseInputClasses} py-2 pr-3`}
          {...props}
        >
          {options.map((opt, i) => (
            <option key={i} value={opt.value}>{opt.label}</option>
          ))}
        </select>
      );
    }

    if (type === 'textarea') {
      return (
        <textarea
          id={inputId}
          ref={ref}
          rows={rows}
          className={`${baseInputClasses} py-2 pr-3`}
          {...props}
        />
      );
    }

    return (
      <input
        type={type}
        id={inputId}
        ref={ref}
        className={`${baseInputClasses} py-2 pr-3`}
        {...props}
      />
    );
  };

  return (
    <div className={`w-full ${className}`}>
      {label && (
        <label htmlFor={inputId} className="block text-sm font-medium text-gray-700 mb-1">
          {label} {required && <span className="text-red-500">*</span>}
        </label>
      )}
      
      <div className="relative rounded-md shadow-sm">
        {IconLeft && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <IconLeft className={`h-5 w-5 ${error ? 'text-red-400' : 'text-gray-400'}`} />
          </div>
        )}
        
        {renderInput()}
      </div>
      
      {error && (
        <p className="mt-1 text-sm text-red-600" id={`${inputId}-error`}>
          {error}
        </p>
      )}
      
      {!error && helperText && (
        <p className="mt-1 text-sm text-gray-500" id={`${inputId}-helper`}>
          {helperText}
        </p>
      )}
    </div>
  );
});

Input.displayName = 'Input';

export default Input;
