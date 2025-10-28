'use client';

import { Transaction } from '@/lib/api';
import { formatCurrency, formatDate, CATEGORY_COLORS } from '@/lib/utils';

interface TransactionsListProps {
  transactions: Transaction[];
  loading: boolean;
  onDelete?: (transactionId: string) => void;
  onSplit?: (transaction: Transaction) => void;
  onViewSplit?: (transaction: Transaction) => void;
  splitTransactions?: Set<string>;
}

export default function TransactionsList({ 
  transactions, 
  loading, 
  onDelete, 
  onSplit, 
  onViewSplit,
  splitTransactions = new Set()
}: TransactionsListProps) {
  if (loading) {
    return (
      <div className="space-y-2">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 p-4 animate-pulse">
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <div className="h-5 bg-gray-200 dark:bg-gray-800 rounded w-1/3 mb-2"></div>
                <div className="h-4 bg-gray-200 dark:bg-gray-800 rounded w-1/4"></div>
              </div>
              <div className="h-6 bg-gray-200 dark:bg-gray-800 rounded w-20"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (transactions.length === 0) {
    return (
      <div className="rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 p-8 text-center">
        <p className="text-gray-500 dark:text-gray-400">
          No transactions found. Try fetching from Gmail or adding manually.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {transactions.map((transaction) => (
        <div
          key={transaction._id}
          className="rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 p-4 hover:shadow-md transition-shadow"
        >
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <h4 className="font-semibold text-gray-900 dark:text-gray-100">
                {transaction.merchant}
              </h4>
              <div className="flex items-center gap-2 mt-1">
                <span
                  className={`text-xs px-2 py-1 rounded-full ${
                    CATEGORY_COLORS[transaction.category] || CATEGORY_COLORS['Others']
                  }`}
                >
                  {transaction.category}
                </span>
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  {formatDate(transaction.date)}
                </span>
              </div>
              {transaction.email_subject && (
                <p className="text-xs text-gray-400 dark:text-gray-500 mt-1 truncate">
                  📧 {transaction.email_subject}
                </p>
              )}
            </div>
            <div className="flex items-start gap-2">
              <div className="text-right">
                <p className="text-lg font-bold text-gray-900 dark:text-gray-100">
                  {formatCurrency(transaction.amount)}
                </p>
              </div>
              
              {/* Split Button */}
              {splitTransactions.has(transaction._id) ? (
                <button
                  onClick={() => onViewSplit?.(transaction)}
                  className="text-green-600 hover:text-green-700 dark:text-green-400 dark:hover:text-green-300 p-1 rounded hover:bg-green-50 dark:hover:bg-green-900/20 transition-colors"
                  title="View split details"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
                    <path fillRule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm9.707 5.707a1 1 0 00-1.414-1.414L9 12.586l-1.293-1.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                </button>
              ) : (
                onSplit && (
                  <button
                    onClick={() => onSplit(transaction)}
                    className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 p-1 rounded hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors"
                    title="Split transaction"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path d="M8 5a1 1 0 100 2h5.586l-1.293 1.293a1 1 0 001.414 1.414l3-3a1 1 0 000-1.414l-3-3a1 1 0 10-1.414 1.414L13.586 5H8zM12 15a1 1 0 100-2H6.414l1.293-1.293a1 1 0 10-1.414-1.414l-3 3a1 1 0 000 1.414l3 3a1 1 0 001.414-1.414L6.414 15H12z" />
                    </svg>
                  </button>
                )
              )}
              
              {/* Delete Button */}
              {onDelete && (
                <button
                  onClick={() => onDelete(transaction._id)}
                  className="text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 p-1 rounded hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                  title="Delete transaction"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                </button>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
