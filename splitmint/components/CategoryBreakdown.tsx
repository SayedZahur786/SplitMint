import { CategorySpending } from '@/lib/api';
import { formatCurrency, CATEGORY_COLORS } from '@/lib/utils';

interface CategoryBreakdownProps {
  breakdown: CategorySpending[];
  total: number;
}

export default function CategoryBreakdown({ breakdown, total }: CategoryBreakdownProps) {
  if (!breakdown || breakdown.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          Category Breakdown
        </h2>
        <p className="text-gray-500 dark:text-gray-400">No spending data available</p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
        Category Breakdown
      </h2>
      
      <div className="space-y-4">
        {breakdown.map((item) => (
          <div key={item.category}>
            <div className="flex justify-between items-center mb-1">
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${CATEGORY_COLORS[item.category] || CATEGORY_COLORS['Unknown']}`}>
                {item.category}
              </span>
              <span className="text-sm font-semibold text-gray-900 dark:text-white">
                {formatCurrency(item.amount)}
              </span>
            </div>
            
            {/* Progress bar */}
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div
                className="bg-blue-600 dark:bg-blue-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${item.percentage}%` }}
              />
            </div>
            
            <div className="flex justify-between items-center mt-1">
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {item.percentage}% of total
              </span>
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
        <div className="flex justify-between items-center">
          <span className="text-lg font-semibold text-gray-900 dark:text-white">
            Total Spending
          </span>
          <span className="text-lg font-bold text-gray-900 dark:text-white">
            {formatCurrency(total)}
          </span>
        </div>
      </div>
    </div>
  );
}
