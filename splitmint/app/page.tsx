'use client';

import { useState, useEffect } from 'react';
import BudgetCard from '@/components/BudgetCard';
import TransactionsList from '@/components/TransactionsList';
import CategoryBreakdown from '@/components/CategoryBreakdown';
import SplitTransactionModal from '@/components/SplitTransactionModal';
import SplitDetailsModal from '@/components/SplitDetailsModal';
import {
  getTransactions,
  getBudget,
  fetchTransactions,
  updateBudget,
  addTransaction,
  deleteTransaction,
  getSpendingByCategory,
  Transaction,
  Budget,
  CategorySpending,
} from '@/lib/api';
import { getCurrentMonth, CATEGORIES } from '@/lib/utils';

export default function Home() {
  const [userId] = useState('demo_user'); // In production, get from auth
  const [month, setMonth] = useState(getCurrentMonth());
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [budget, setBudget] = useState<Budget | null>(null);
  const [categoryBreakdown, setCategoryBreakdown] = useState<CategorySpending[]>([]);
  const [totalSpending, setTotalSpending] = useState(0);
  const [loading, setLoading] = useState(true);
  const [budgetLoading, setBudgetLoading] = useState(true);
  const [message, setMessage] = useState('');

  // Budget form state
  const [showBudgetForm, setShowBudgetForm] = useState(false);
  const [budgetIncome, setBudgetIncome] = useState('');
  const [budgetAmount, setBudgetAmount] = useState('');

  // Transaction form state
  const [showTransactionForm, setShowTransactionForm] = useState(false);
  const [merchant, setMerchant] = useState('');
  const [amount, setAmount] = useState('');
  const [category, setCategory] = useState(CATEGORIES[0]);
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);

  // Split transaction state
  const [showSplitModal, setShowSplitModal] = useState(false);
  const [showSplitDetailsModal, setShowSplitDetailsModal] = useState(false);
  const [selectedTransaction, setSelectedTransaction] = useState<Transaction | null>(null);
  const [splitTransactions, setSplitTransactions] = useState<Set<string>>(new Set());
  const [currentSplit, setCurrentSplit] = useState<any>(null);

  useEffect(() => {
    loadTransactions();
    loadBudget();
    loadCategoryBreakdown();
    loadSplits();
  }, [month]);

  const loadTransactions = async () => {
    setLoading(true);
    try {
      const response = await getTransactions(userId, month);
      if (response.success && response.data) {
        setTransactions(response.data.transactions);
      }
    } catch (error) {
      console.error('Error loading transactions:', error);
    }
    setLoading(false);
  };

  const loadBudget = async () => {
    setBudgetLoading(true);
    try {
      const response = await getBudget(userId, month);
      if (response.success && response.data) {
        setBudget(response.data);
      } else {
        setBudget(null);
      }
    } catch (error) {
      setBudget(null);
    }
    setBudgetLoading(false);
  };

  const loadCategoryBreakdown = async () => {
    try {
      const response = await getSpendingByCategory(userId, month);
      if (response.success && response.data) {
        setCategoryBreakdown(response.data.breakdown);
        setTotalSpending(response.data.total);
      }
    } catch (error) {
      console.error('Error loading category breakdown:', error);
    }
  };

  const loadSplits = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/splits/${userId}`);
      const data = await response.json();
      if (data.success && data.data) {
        const splitIds = new Set<string>(data.data.map((split: any) => split.transaction_id));
        setSplitTransactions(splitIds);
      }
    } catch (error) {
      console.error('Error loading splits:', error);
    }
  };

  const handleSplitTransaction = (transaction: Transaction) => {
    setSelectedTransaction(transaction);
    setShowSplitModal(true);
  };

  const handleViewSplit = async (transaction: Transaction) => {
    try {
      const response = await fetch('http://localhost:8000/api/get-split', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          transaction_id: transaction._id
        })
      });
      const data = await response.json();
      if (data.success && data.data) {
        setCurrentSplit(data.data);
        setShowSplitDetailsModal(true);
      }
    } catch (error) {
      console.error('Error loading split details:', error);
    }
  };

  const handleSplitCreated = () => {
    loadSplits();
  };

  const handleDeleteSplit = async () => {
    if (!currentSplit || !confirm('Are you sure you want to delete this split?')) {
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/api/delete-split', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          transaction_id: currentSplit.transaction_id
        })
      });
      const data = await response.json();
      if (data.success) {
        setShowSplitDetailsModal(false);
        setCurrentSplit(null);
        loadSplits();
        setMessage('Split deleted successfully');
        setTimeout(() => setMessage(''), 3000);
      }
    } catch (error) {
      setMessage('Error deleting split');
      setTimeout(() => setMessage(''), 3000);
    }
  };

  const handleFetchFromGmail = async () => {
    setMessage('Fetching transactions from Gmail...');
    try {
      const response = await fetchTransactions(userId);
      setMessage(response.message);
      if (response.success) {
        loadTransactions();
        loadBudget();
        loadCategoryBreakdown();
      }
    } catch (error) {
      setMessage('Error fetching from Gmail');
    }
    setTimeout(() => setMessage(''), 5000);
  };

  const handleUpdateBudget = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage('Updating budget...');
    try {
      const response = await updateBudget(
        userId,
        parseFloat(budgetIncome),
        parseFloat(budgetAmount),
        month
      );
      setMessage(response.message);
      if (response.success) {
        loadBudget();
        setShowBudgetForm(false);
        setBudgetIncome('');
        setBudgetAmount('');
      }
    } catch (error) {
      setMessage('Error updating budget');
    }
    setTimeout(() => setMessage(''), 5000);
  };

  const handleAddTransaction = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage('Adding transaction...');
    try {
      const response = await addTransaction(
        userId,
        merchant,
        parseFloat(amount),
        category,
        date
      );
      setMessage(response.message);
      if (response.success) {
        loadTransactions();
        loadBudget();
        loadCategoryBreakdown();
        setShowTransactionForm(false);
        setMerchant('');
        setAmount('');
        setCategory(CATEGORIES[0]);
        setDate(new Date().toISOString().split('T')[0]);
      }
    } catch (error) {
      setMessage('Error adding transaction');
    }
    setTimeout(() => setMessage(''), 5000);
  };

  const handleDeleteTransaction = async (transactionId: string) => {
    if (!confirm('Are you sure you want to delete this transaction?')) {
      return;
    }

    setMessage('Deleting transaction...');
    try {
      const response = await deleteTransaction(userId, transactionId);
      setMessage(response.message);
      if (response.success) {
        loadTransactions();
        loadBudget();
        loadCategoryBreakdown();
      }
    } catch (error) {
      setMessage('Error deleting transaction');
    }
    setTimeout(() => setMessage(''), 5000);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            SplitMint 💰
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Your smart expense tracker with Gmail integration
          </p>
        </div>

        {/* Message Banner */}
        {message && (
          <div className="mb-6 p-4 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-lg">
            {message}
          </div>
        )}

        {/* Action Buttons */}
        <div className="mb-6 flex flex-wrap gap-3">
          <button
            onClick={handleFetchFromGmail}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            📧 Fetch from Gmail
          </button>
          <button
            onClick={() => setShowBudgetForm(!showBudgetForm)}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            💵 Set Budget
          </button>
          <button
            onClick={() => setShowTransactionForm(!showTransactionForm)}
            className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
          >
            ➕ Add Transaction
          </button>
        </div>

        {/* Budget Form */}
        {showBudgetForm && (
          <div className="mb-6 p-6 bg-white dark:bg-gray-950 rounded-lg border border-gray-200 dark:border-gray-800">
            <h3 className="text-lg font-semibold mb-4">Set Monthly Budget</h3>
            <form onSubmit={handleUpdateBudget} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Income (₹)</label>
                  <input
                    type="number"
                    value={budgetIncome}
                    onChange={(e) => setBudgetIncome(e.target.value)}
                    required
                    min="0"
                    step="0.01"
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg dark:bg-gray-900"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Budget (₹)</label>
                  <input
                    type="number"
                    value={budgetAmount}
                    onChange={(e) => setBudgetAmount(e.target.value)}
                    required
                    min="0"
                    step="0.01"
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg dark:bg-gray-900"
                  />
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  type="submit"
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                >
                  Save Budget
                </button>
                <button
                  type="button"
                  onClick={() => setShowBudgetForm(false)}
                  className="px-4 py-2 bg-gray-300 dark:bg-gray-700 rounded-lg hover:bg-gray-400 dark:hover:bg-gray-600"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Transaction Form */}
        {showTransactionForm && (
          <div className="mb-6 p-6 bg-white dark:bg-gray-950 rounded-lg border border-gray-200 dark:border-gray-800">
            <h3 className="text-lg font-semibold mb-4">Add Transaction</h3>
            <form onSubmit={handleAddTransaction} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Merchant</label>
                  <input
                    type="text"
                    value={merchant}
                    onChange={(e) => setMerchant(e.target.value)}
                    required
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg dark:bg-gray-900"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Amount (₹)</label>
                  <input
                    type="number"
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    required
                    min="0"
                    step="0.01"
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg dark:bg-gray-900"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Category</label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg dark:bg-gray-900"
                  >
                    {CATEGORIES.map((cat) => (
                      <option key={cat} value={cat}>
                        {cat}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Date</label>
                  <input
                    type="date"
                    value={date}
                    onChange={(e) => setDate(e.target.value)}
                    required
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg dark:bg-gray-900"
                  />
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  type="submit"
                  className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700"
                >
                  Add Transaction
                </button>
                <button
                  type="button"
                  onClick={() => setShowTransactionForm(false)}
                  className="px-4 py-2 bg-gray-300 dark:bg-gray-700 rounded-lg hover:bg-gray-400 dark:hover:bg-gray-600"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Budget Card */}
          <div className="lg:col-span-1">
            <BudgetCard budget={budget} loading={budgetLoading} />
          </div>

          {/* Transactions List */}
          <div className="lg:col-span-2">
            <div className="mb-4 flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                Transactions
              </h2>
              <input
                type="month"
                value={month}
                onChange={(e) => setMonth(e.target.value)}
                className="px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg dark:bg-gray-900"
              />
            </div>
            <TransactionsList 
              transactions={transactions} 
              loading={loading}
              onDelete={handleDeleteTransaction}
              onSplit={handleSplitTransaction}
              onViewSplit={handleViewSplit}
              splitTransactions={splitTransactions}
            />
          </div>
        </div>

        {/* Category Breakdown */}
        <div className="mt-6">
          <CategoryBreakdown breakdown={categoryBreakdown} total={totalSpending} />
        </div>
      </div>

      {/* Split Transaction Modal */}
      {selectedTransaction && (
        <SplitTransactionModal
          isOpen={showSplitModal}
          onClose={() => {
            setShowSplitModal(false);
            setSelectedTransaction(null);
          }}
          transaction={selectedTransaction}
          userId={userId}
          onSplitCreated={handleSplitCreated}
        />
      )}

      {/* Split Details Modal */}
      <SplitDetailsModal
        isOpen={showSplitDetailsModal}
        onClose={() => {
          setShowSplitDetailsModal(false);
          setCurrentSplit(null);
        }}
        split={currentSplit}
        onDelete={handleDeleteSplit}
      />
    </div>
  );
}
