import { useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Select } from '../ui/Select';
import { toast } from 'react-toastify';
import api from '../../utils/api';

const CATEGORIES = [
  { value: 'Food', label: 'Food & Dining' },
  { value: 'Transport', label: 'Transportation' },
  { value: 'Utilities', label: 'Utilities' },
  { value: 'Entertainment', label: 'Entertainment' },
  { value: 'Health', label: 'Health' },
  { value: 'Other', label: 'Other' },
];

export default function ExpenseForm({ onSuccess, initialData, onCancel, isModal }) {
  const [loading, setLoading] = useState(false);
  const [clientId, setClientId] = useState('');
  
  const [formData, setFormData] = useState({
    amount: '',
    category: 'Food',
    description: '',
    // Use strictly YYYY-MM-DD for the date input
    date: new Date().toISOString().slice(0, 10)
  });

  useEffect(() => {
    if (initialData) {
      setFormData({
        amount: initialData.amount,
        category: initialData.category,
        description: initialData.description || '',
        // Extract YYYY-MM-DD from ISO string
        date: initialData.date.slice(0, 10)
      });
      setClientId(''); 
    } else {
      setFormData({ 
        amount: '', 
        category: 'Food', 
        description: '', 
        date: new Date().toISOString().slice(0, 10) 
      });
      setClientId(uuidv4());
    }
  }, [initialData]);

  useEffect(() => {
    if (!initialData && !clientId) {
      setClientId(uuidv4());
    }
  }, [initialData, clientId]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Backend expects ISO DateTime, but we only picked Date.
      // Append time to make it a valid ISO string.
      const payload = {
        ...formData,
        date: new Date(formData.date).toISOString(), 
      };

      if (initialData) {
        await api.put(`/expenses/${initialData.id}`, payload);
        toast.success('Transaction updated');
      } else {
        payload.client_id = clientId;
        await api.post('/expenses', payload);
        toast.success('Transaction added');
        setClientId(uuidv4());
      }
      
      // Reset
      setFormData({ amount: '', category: 'Food', description: '', date: new Date().toISOString().slice(0, 10) });
      
      if (onSuccess) onSuccess();
    } catch (error) {
      console.error(error);
      const msg = error.response?.data?.detail?.[0]?.msg || 'Operation failed';
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  // If in modal, remove container styling (the modal handles it)
  const containerClass = isModal ? "" : "bg-white p-6 rounded-xl shadow-sm border border-slate-100";

  return (
    <form onSubmit={handleSubmit} className={containerClass}>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div className="md:col-span-2">
          <Input 
            label="Amount (₹)" 
            type="number" 
            step="0.01" 
            required 
            placeholder="0.00"
            className="text-lg font-semibold"
            value={formData.amount}
            onChange={e => setFormData({...formData, amount: e.target.value})}
          />
        </div>
        
        <div className="md:col-span-2">
            <Select 
            label="Category" 
            options={CATEGORIES}
            value={formData.category}
            onChange={e => setFormData({...formData, category: e.target.value})}
            />
        </div>

        <div className="md:col-span-2">
          <Input 
            label="Date" 
            type="date" // Strictly date picker
            required
            value={formData.date}
            onChange={e => setFormData({...formData, date: e.target.value})}
          />
        </div>

        <div className="md:col-span-2">
          <Input 
            label="Description (Optional)" 
            placeholder="What was this for?"
            value={formData.description}
            onChange={e => setFormData({...formData, description: e.target.value})}
          />
        </div>
      </div>

      <div className="mt-8 flex gap-3 justify-end pt-4 border-t border-slate-50">
        <Button type="button" variant="secondary" onClick={onCancel} disabled={loading}>
          Cancel
        </Button>
        <Button type="submit" isLoading={loading} className="px-8">
          {initialData ? 'Update' : 'Save'}
        </Button>
      </div>
    </form>
  );
}