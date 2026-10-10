import React from 'react';
import { ArrowUp, ArrowDown } from 'lucide-react';

const Table = ({ 
  columns, 
  data, 
  isLoading = false, 
  emptyMessage = "No data available", 
  onRowClick,
  sortColumn,
  sortDirection,
  onSort
}) => {
  if (isLoading) {
    return (
      <div className="animate-pulse flex flex-col gap-4">
        <div className="h-10 bg-gray-200 rounded w-full"></div>
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-12 bg-gray-100 rounded w-full"></div>
        ))}
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="text-center py-12 px-4 border border-gray-200 rounded-lg bg-gray-50">
        <p className="text-gray-500">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto border border-gray-200 rounded-lg">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            {columns.map((col, index) => (
              <th 
                key={col.key || index}
                scope="col" 
                className={`px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider ${col.sortable && onSort ? 'cursor-pointer hover:bg-gray-100' : ''}`}
                onClick={() => col.sortable && onSort && onSort(col.key)}
              >
                <div className="flex items-center space-x-1">
                  <span>{col.label}</span>
                  {col.sortable && sortColumn === col.key && (
                    <span>
                      {sortDirection === 'asc' ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />}
                    </span>
                  )}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {data.map((row, rowIndex) => (
            <tr 
              key={row.id || rowIndex} 
              className={onRowClick ? "hover:bg-gray-50 cursor-pointer transition-colors" : ""}
              onClick={() => onRowClick && onRowClick(row)}
            >
              {columns.map((col, colIndex) => (
                <td key={col.key || colIndex} className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                  {col.render ? col.render(row[col.key], row) : row[col.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Table;
