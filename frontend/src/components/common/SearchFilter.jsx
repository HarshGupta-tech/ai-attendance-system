import React from 'react';
import { Search, Filter, X } from 'lucide-react';
import Button from './Button';

const SearchFilter = ({ 
  searchValue, 
  onSearchChange, 
  filters = [], 
  onFilterChange, 
  onClearFilters,
  placeholder = "Search..." 
}) => {
  const hasActiveFilters = filters.some(f => f.value !== '');

  return (
    <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200 mb-6">
      <div className="flex flex-col md:flex-row md:items-center gap-4">
        {/* Search Input */}
        <div className="flex-1 relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm transition-colors"
            placeholder={placeholder}
            value={searchValue}
            onChange={(e) => onSearchChange(e.target.value)}
          />
        </div>

        {/* Filters */}
        {filters.length > 0 && (
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center text-gray-500 text-sm font-medium">
              <Filter className="h-4 w-4 mr-1" />
              Filters:
            </div>
            
            {filters.map((filter, index) => (
              <select
                key={index}
                className="block pl-3 pr-8 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                value={filter.value}
                onChange={(e) => onFilterChange(filter.key, e.target.value)}
              >
                <option value="">{filter.label}</option>
                {filter.options.map((opt, i) => (
                  <option key={i} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            ))}

            {(hasActiveFilters || searchValue) && (
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={onClearFilters}
                iconLeft={<X className="h-4 w-4" />}
              >
                Clear
              </Button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchFilter;
