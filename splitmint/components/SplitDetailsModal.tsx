'use client';

import { formatCurrency, sendWhatsAppMessage, createSettlementWhatsAppMessage } from '@/lib/utils';

interface Participant {
  name: string;
  phone_number?: string;
  amount_paid: number;
  share_amount: number;
  amount_owed: number;
  share_percentage: number;
}

interface SplitDetailsModalProps {
  isOpen: boolean;
  onClose: () => void;
  split: {
    transaction_id: string;
    merchant: string;
    total_amount: number;
    category: string;
    date: string;
    split_method: string;
    participants: Participant[];
    notes?: string;
    created_at: string;
    updated_at: string;
  } | null;
  onDelete?: () => void;
}

export default function SplitDetailsModal({
  isOpen,
  onClose,
  split,
  onDelete
}: SplitDetailsModalProps) {
  if (!isOpen || !split) return null;

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    });
  };

  const handleSendReminder = (participant: Participant) => {
    if (!participant.phone_number) {
      alert('Phone number not available for this participant');
      return;
    }

    // Find who should receive the payment (person who paid more or gets money back)
    const receiver = split.participants.find(p => p.amount_owed < 0);
    if (!receiver) {
      alert('Unable to determine payment receiver');
      return;
    }

    const message = createSettlementWhatsAppMessage(
      participant.name,
      receiver.name,
      participant.amount_owed,
      split.merchant
    );

    sendWhatsAppMessage(participant.phone_number, message);
  };

  const handleSendAllReminders = () => {
    const participantsWhoOwe = split.participants.filter(p => p.amount_owed > 0 && p.phone_number);
    
    if (participantsWhoOwe.length === 0) {
      alert('No participants with phone numbers owe money');
      return;
    }

    const receiver = split.participants.find(p => p.amount_owed < 0);
    if (!receiver) {
      alert('Unable to determine payment receiver');
      return;
    }

    // Send to all participants who owe money
    participantsWhoOwe.forEach(participant => {
      const message = createSettlementWhatsAppMessage(
        participant.name,
        receiver.name,
        participant.amount_owed,
        split.merchant
      );
      setTimeout(() => {
        sendWhatsAppMessage(participant.phone_number!, message);
      }, 500); // Small delay between messages
    });

    alert(`Sending reminders to ${participantsWhoOwe.length} participant(s)`);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-6">
          <div className="flex justify-between items-start">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Split Details</h2>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                {split.merchant} • {formatCurrency(split.total_amount)}
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
          {/* Transaction Info */}
          <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div>
              <p className="text-xs text-gray-600 dark:text-gray-400">Date</p>
              <p className="text-sm font-medium text-gray-900 dark:text-white">{formatDate(split.date)}</p>
            </div>
            <div>
              <p className="text-xs text-gray-600 dark:text-gray-400">Category</p>
              <p className="text-sm font-medium text-gray-900 dark:text-white">{split.category}</p>
            </div>
            <div>
              <p className="text-xs text-gray-600 dark:text-gray-400">Split Method</p>
              <p className="text-sm font-medium text-gray-900 dark:text-white capitalize">{split.split_method}</p>
            </div>
            <div>
              <p className="text-xs text-gray-600 dark:text-gray-400">Participants</p>
              <p className="text-sm font-medium text-gray-900 dark:text-white">{split.participants.length} people</p>
            </div>
          </div>

          {/* Participants */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">Participants</h3>
            <div className="space-y-3">
              {split.participants.map((participant, index) => (
                <div
                  key={index}
                  className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg"
                >
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h4 className="font-semibold text-gray-900 dark:text-white">{participant.name}</h4>
                      {participant.phone_number && (
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          📞 {participant.phone_number}
                        </p>
                      )}
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {participant.share_percentage.toFixed(1)}% share
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-gray-600 dark:text-gray-400">Share Amount</p>
                      <p className="text-lg font-bold text-gray-900 dark:text-white">
                        {formatCurrency(participant.share_amount)}
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3 pt-3 border-t border-gray-100 dark:border-gray-600">
                    <div>
                      <p className="text-xs text-gray-600 dark:text-gray-400">Amount Paid</p>
                      <p className="text-sm font-medium text-green-600 dark:text-green-400">
                        {formatCurrency(participant.amount_paid)}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-600 dark:text-gray-400">
                        {participant.amount_owed >= 0 ? 'Owes' : 'Gets Back'}
                      </p>
                      <p className={`text-sm font-medium ${
                        participant.amount_owed >= 0 
                          ? 'text-red-600 dark:text-red-400' 
                          : 'text-green-600 dark:text-green-400'
                      }`}>
                        {formatCurrency(Math.abs(participant.amount_owed))}
                      </p>
                    </div>
                  </div>

                  {/* WhatsApp Reminder Button */}
                  {participant.amount_owed > 0 && participant.phone_number && (
                    <div className="mt-3 pt-3 border-t border-gray-100 dark:border-gray-600">
                      <button
                        onClick={() => handleSendReminder(participant)}
                        className="w-full px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg flex items-center justify-center gap-2 transition-colors"
                      >
                        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
                        </svg>
                        Send WhatsApp Reminder
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Settlement Summary */}
          <div className="p-4 bg-blue-50 dark:bg-blue-900 rounded-lg">
            <div className="flex justify-between items-center mb-3">
              <h3 className="text-sm font-semibold text-blue-900 dark:text-blue-200">
                Settlement Summary
              </h3>
              {split.participants.some(p => p.amount_owed > 0 && p.phone_number) && (
                <button
                  onClick={handleSendAllReminders}
                  className="px-3 py-1 text-xs bg-green-500 hover:bg-green-600 text-white rounded-md flex items-center gap-1 transition-colors"
                >
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
                  </svg>
                  Send All
                </button>
              )}
            </div>
            <div className="space-y-2 text-sm text-blue-800 dark:text-blue-200">
              {split.participants
                .filter(p => p.amount_owed > 0)
                .map((payer, index) => {
                  const receiver = split.participants.find(p => p.amount_owed < 0);
                  if (!receiver) return null;
                  
                  return (
                    <div key={index} className="flex items-center gap-2">
                      <span className="font-medium">{payer.name}</span>
                      <span>→</span>
                      <span className="font-medium">{receiver.name}</span>
                      <span className="ml-auto font-bold">
                        {formatCurrency(Math.min(payer.amount_owed, Math.abs(receiver.amount_owed)))}
                      </span>
                    </div>
                  );
                })}
            </div>
          </div>

          {/* Notes */}
          {split.notes && (
            <div>
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">Notes</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                {split.notes}
              </p>
            </div>
          )}

          {/* Metadata */}
          <div className="text-xs text-gray-500 dark:text-gray-400 pt-4 border-t border-gray-200 dark:border-gray-700">
            <p>Created: {formatDate(split.created_at)}</p>
            {split.updated_at !== split.created_at && (
              <p>Updated: {formatDate(split.updated_at)}</p>
            )}
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
            <button
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 font-medium"
            >
              Close
            </button>
            {onDelete && (
              <button
                onClick={onDelete}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 font-medium"
              >
                Delete Split
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
