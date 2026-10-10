import React from 'react';

const Card = ({ 
  title, 
  subtitle, 
  icon: Icon, 
  children, 
  footer, 
  hoverEffect = false,
  padding = 'normal',
  className = '' 
}) => {
  const paddingClasses = {
    none: '',
    small: 'p-4',
    normal: 'p-6',
    large: 'p-8'
  };

  return (
    <div className={`bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden ${hoverEffect ? 'card-hover' : ''} ${className}`}>
      {(title || subtitle || Icon) && (
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between bg-white">
          <div>
            {title && <h3 className="text-lg font-medium leading-6 text-gray-900">{title}</h3>}
            {subtitle && <p className="mt-1 text-sm text-gray-500">{subtitle}</p>}
          </div>
          {Icon && (
            <div className="p-2 bg-indigo-50 rounded-lg">
              <Icon className="h-6 w-6 text-indigo-600" />
            </div>
          )}
        </div>
      )}
      
      <div className={paddingClasses[padding]}>
        {children}
      </div>
      
      {footer && (
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
          {footer}
        </div>
      )}
    </div>
  );
};

export default Card;
