'use client';

import { useState, useEffect } from 'react';
import { formatCurrency } from '@/lib/utils';

interface Participant {
  name: string;
  phone_number?: string;
  share_percentage?: number;
  share_ratio?: number;
  amount_paid: number;
  share_amount?: number;
  amount_owed?: number;
}

interface SplitTransactionModalProps {
  isOpen: boolean;
  onClose: () => void;
  transaction: {
    _id: string;
    merchant: string;
    amount: number;
    category: string;
    date: string;
  };
  userId: string;
  onSplitCreated?: () => void;
}

export default function SplitTransactionModal({
  isOpen,
  onClose,
  transaction,
  userId,
  onSplitCreated
}: SplitTransactionModalProps) {
  const [splitMethod, setSplitMethod] = useState<'equal' | 'percentage' | 'ratio'>('equal');
  const [participants, setParticipants] = useState<Participant[]>([
    { name: 'You', phone_number: '', amount_paid: transaction.amount, share_percentage: 50, share_ratio: 1 },
    { name: '', phone_number: '', amount_paid: 0, share_percentage: 50, share_ratio: 1 }
  ]);
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Reset form when transaction changes
  useEffect(() => {
    if (isOpen) {
      setParticipants([
        { name: 'You', phone_number: '', amount_paid: transaction.amount, share_percentage: 50, share_ratio: 1 },
        { name: '', phone_number: '', amount_paid: 0, share_percentage: 50, share_ratio: 1 }
      ]);
      setSplitMethod('equal');
      setNotes('');
      setError('');
    }
  }, [transaction, isOpen]);

  const addParticipant = () => {
    const newPercentage = 100 / (participants.length + 1);
    setParticipants([
      ...participants.map(p => ({ ...p, share_percentage: newPercentage })),
      { name: '', phone_number: '', amount_paid: 0, share_percentage: newPercentage, share_ratio: 1 }
    ]);
  };

  const removeParticipant = (index: number) => {
    if (participants.length <= 2) {
      setError('At least 2 participants required');
      return;
    }
    const newParticipants = participants.filter((_, i) => i !== index);
    const newPercentage = 100 / newParticipants.length;
    setParticipants(newParticipants.map(p => ({ ...p, share_percentage: newPercentage })));
  };

  const updateParticipant = (index: number, field: keyof Participant, value: string | number) => {
    const newParticipants = [...participants];
    newParticipants[index] = { ...newParticipants[index], [field]: value };
    setParticipants(newParticipants);
  };

  const validateAndSubmit = async () => {
    setError('');

    // Validate participant names
    if (participants.some(p => !p.name.trim())) {
      setError('All participants must have names');
      return;
    }

    // Validate total paid
    const totalPaid = participants.reduce((sum, p) => sum + (Number(p.amount_paid) || 0), 0);
    if (Math.abs(totalPaid - transaction.amount) > 0.01) {
      setError(`Total paid (${formatCurrency(totalPaid)}) must equal transaction amount (${formatCurrency(transaction.amount)})`);
      return;
    }

    // Validate percentages for percentage split
    if (splitMethod === 'percentage') {
      const totalPercentage = participants.reduce((sum, p) => sum + (Number(p.share_percentage) || 0), 0);
      if (Math.abs(totalPercentage - 100) > 0.01) {
        setError(`Percentages must add up to 100% (currently ${totalPercentage.toFixed(1)}%)`);
        return;
      }
    }

    // Submit
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/create-split', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          transaction_id: transaction._id,
          participants: participants,
          split_method: splitMethod,
          notes: notes || null
        })
      });

      const data = await response.json();

      if (data.success) {
        onSplitCreated?.();
        onClose();
      } else {
        setError(data.message || 'Failed to create split');
      }
    } catch (err) {
      setError('Network error. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-6">
          <div className="flex justify-between items-start">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Split Transaction</h2>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                {transaction.merchant} • {formatCurrency(transaction.amount)}
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Split Method */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Split Method
            </label>
            <div className="grid grid-cols-3 gap-3">
              {(['equal', 'percentage', 'ratio'] as const).map((method) => (
                <button
                  key={method}
                  onClick={() => setSplitMethod(method)}
                  className={`px-4 py-2 rounded-lg border-2 font-medium capitalize transition ${
                    splitMethod === method
                      ? 'border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-900 dark:text-blue-200'
                      : 'border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:border-gray-400'
                  }`}
                >
                  {method}
                </button>
              ))}
            </div>
          </div>

          {/* Participants */}
          <div>
            <div className="flex justify-between items-center mb-3">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Participants
              </label>
              <button
                onClick={addParticipant}
                className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 font-medium"
              >
                + Add Person
              </button>
            </div>

            <div className="space-y-3">
              {participants.map((participant, index) => (
                <div key={index} className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                  <div className="grid grid-cols-12 gap-3">
                    {/* Name */}
                    <div className="col-span-12 sm:col-span-3">
                      <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">Name</label>
                      <input
                        type="text"
                        value={participant.name}
                        onChange={(e) => updateParticipant(index, 'name', e.target.value)}
                        placeholder="Name"
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                      />
                    </div>

                    {/* Phone Number */}
                    <div className="col-span-12 sm:col-span-3">
                      <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">Phone</label>
                      <input
                        type="tel"
                        value={participant.phone_number || ''}
                        onChange={(e) => updateParticipant(index, 'phone_number', e.target.value)}
                        placeholder="+91 XXXXX XXXXX"
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                      />
                    </div>

                    {/* Amount Paid */}
                    <div className="col-span-6 sm:col-span-2">
                      <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">Paid</label>
                      <input
                        type="number"
                        value={participant.amount_paid}
                        onChange={(e) => updateParticipant(index, 'amount_paid', parseFloat(e.target.value) || 0)}
                        placeholder="0"
                        step="0.01"
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                      />
                    </div>

                    {/* Share (Percentage or Ratio) */}
                    {splitMethod === 'percentage' && (
                      <div className="col-span-6 sm:col-span-2">
                        <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">Share %</label>
                        <input
                          type="number"
                          value={participant.share_percentage}
                          onChange={(e) => updateParticipant(index, 'share_percentage', parseFloat(e.target.value) || 0)}
                          placeholder="0"
                          step="0.1"
                          max="100"
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                        />
                      </div>
                    )}

                    {splitMethod === 'ratio' && (
                      <div className="col-span-6 sm:col-span-2">
                        <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">Ratio</label>
                        <input
                          type="number"
                          value={participant.share_ratio}
                          onChange={(e) => updateParticipant(index, 'share_ratio', parseInt(e.target.value) || 1)}
                          placeholder="1"
                          min="1"
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                        />
                      </div>
                    )}

                    {splitMethod === 'equal' && (
                      <div className="col-span-6 sm:col-span-2 flex items-end">
                        <div className="w-full px-3 py-2 bg-gray-100 dark:bg-gray-600 rounded-md text-gray-600 dark:text-gray-300 text-sm">
                          Equal share
                        </div>
                      </div>
                    )}

                    {/* Remove Button */}
                    <div className="col-span-12 sm:col-span-2 flex items-end">
                      <button
                        onClick={() => removeParticipant(index)}
                        disabled={participants.length <= 2}
                        className="w-full px-3 py-2 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900 rounded-md disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Summary */}
            <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900 rounded-lg">
              <div className="text-sm text-blue-800 dark:text-blue-200">
                <div className="flex justify-between">
                  <span>Total Amount:</span>
                  <span className="font-semibold">{formatCurrency(transaction.amount)}</span>
                </div>
                <div className="flex justify-between mt-1">
                  <span>Total Paid:</span>
                  <span className={`font-semibold ${
                    Math.abs(participants.reduce((sum, p) => sum + (Number(p.amount_paid) || 0), 0) - transaction.amount) > 0.01
                      ? 'text-red-600 dark:text-red-400'
                      : 'text-green-600 dark:text-green-400'
                  }`}>
                    {formatCurrency(participants.reduce((sum, p) => sum + (Number(p.amount_paid) || 0), 0))}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Notes (Optional)
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Add any notes about this split..."
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
          </div>

          {/* Error */}
          {error && (
            <div className="p-3 bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-lg">
              <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
            <button
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 font-medium"
            >
              Cancel
            </button>
            <button
              onClick={validateAndSubmit}
              disabled={loading}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Creating Split...' : 'Create Split'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
