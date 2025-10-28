'use client';

import { Budget } from '@/lib/api';
import { formatCurrency, getMonthName } from '@/lib/utils';

interface BudgetCardProps {
  budget: Budget | null;
  loading: boolean;
}

export default function BudgetCard({ budget, loading }: BudgetCardProps) {
  if (loading) {
    return (
      <div className="rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 p-6 shadow-sm animate-pulse">
        <div className="h-6 bg-gray-200 dark:bg-gray-800 rounded w-1/3 mb-4"></div>
        <div className="h-12 bg-gray-200 dark:bg-gray-800 rounded w-1/2 mb-6"></div>
        <div className="space-y-3">
          <div className="h-4 bg-gray-200 dark:bg-gray-800 rounded"></div>
          <div className="h-4 bg-gray-200 dark:bg-gray-800 rounded"></div>
        </div>
      </div>
    );
  }

  if (!budget) {
    return (
      <div className="rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 p-6 shadow-sm">
        <p className="text-gray-500 dark:text-gray-400 text-center">
          No budget set for this month
        </p>
      </div>
    );
  }

  const percentage = (budget.total_spent / budget.budget) * 100;
  const isOverBudget = budget.remaining < 0;

  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 p-6 shadow-sm">
      <div className="mb-4">
        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">
          Budget for {getMonthName(budget.month)}
        </h3>
        <p className="text-3xl font-bold mt-1">
          {formatCurrency(budget.budget)}
        </p>
      </div>

      <div className="space-y-3">
        <div className="flex justify-between text-sm">
          <span className="text-gray-600 dark:text-gray-400">Spent</span>
          <span className="font-semibold">{formatCurrency(budget.total_spent)}</span>
        </div>

        <div className="w-full bg-gray-200 dark:bg-gray-800 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all ${
              isOverBudget ? 'bg-red-500' : percentage > 80 ? 'bg-yellow-500' : 'bg-green-500'
            }`}
            style={{ width: `${Math.min(percentage, 100)}%` }}
          ></div>
        </div>

        <div className="flex justify-between text-sm">
          <span className="text-gray-600 dark:text-gray-400">Remaining</span>
          <span className={`font-semibold ${isOverBudget ? 'text-red-500' : 'text-green-600 dark:text-green-400'}`}>
            {formatCurrency(Math.abs(budget.remaining))}
            {isOverBudget && ' over'}
          </span>
        </div>

        <div className="flex justify-between text-sm pt-2 border-t border-gray-200 dark:border-gray-800">
          <span className="text-gray-600 dark:text-gray-400">Income</span>
          <span className="font-semibold">{formatCurrency(budget.income)}</span>
        </div>
      </div>
    </div>
  );
}
