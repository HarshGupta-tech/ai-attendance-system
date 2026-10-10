import React from 'react';
import { ArrowUp, ArrowDown } from 'lucide-react';
import Card from './Card';

const StatsCard = ({ 
  title, 
  value, 
  icon: Icon, 
  change, 
  changeType = 'neutral', // 'positive', 'negative', 'neutral'
  subtitle,
  iconBgColor = 'bg-indigo-100',
  iconColor = 'text-indigo-600'
}) => {
  return (
    <Card hoverEffect={true}>
      <div className="flex items-center">
        <div className={`flex-shrink-0 rounded-md p-3 ${iconBgColor}`}>
          <Icon className={`h-6 w-6 ${iconColor}`} />
        </div>
        <div className="ml-5 w-0 flex-1">
          <dl>
            <dt className="text-sm font-medium text-gray-500 truncate">{title}</dt>
            <dd>
              <div className="text-2xl font-bold text-gray-900">{value}</div>
            </dd>
          </dl>
        </div>
      </div>
      
      {(change || subtitle) && (
        <div className="mt-4 pt-4 border-t border-gray-100 flex items-center justify-between">
          {change && (
            <div className={`flex items-center text-sm font-medium ${
              changeType === 'positive' ? 'text-green-600' : 
              changeType === 'negative' ? 'text-red-600' : 'text-gray-500'
            }`}>
              {changeType === 'positive' && <ArrowUp className="self-center flex-shrink-0 h-4 w-4 mr-1" />}
              {changeType === 'negative' && <ArrowDown className="self-center flex-shrink-0 h-4 w-4 mr-1" />}
              {change}
            </div>
          )}
          {subtitle && (
            <div className="text-sm text-gray-500 ml-auto">{subtitle}</div>
          )}
        </div>
      )}
    </Card>
  );
};

export default StatsCard;
