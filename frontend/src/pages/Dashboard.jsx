import { useState, useEffect, useCallback } from 'react';
import { Filter, ArrowUpDown, Plus, Trash2 } from 'lucide-react';
import { toast } from 'react-toastify';
import api from '../utils/api';
import ExpenseForm from '../components/expenses/ExpenseForm';
import ExpenseList from '../components/expenses/ExpenseList';
import ExpenseSummary from '../components/expenses/ExpenseSummary';
import Modal from '../components/ui/Modal';
import { Button } from '../components/ui/Button';

const CATEGORIES = ['All', 'Food', 'Transport', 'Utilities', 'Entertainment', 'Health', 'Other'];

export default function Dashboard() {
  const [expenses, setExpenses] = useState([]);
  const [serverTotal, setServerTotal] = useState("0");
  const [loading, setLoading] = useState(true);
  const [filterCat, setFilterCat] = useState('All');
  const [sortOrder, setSortOrder] = useState('date_desc');
  
  // Modal States
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingExpense, setEditingExpense] = useState(null);
  const [deleteId, setDeleteId] = useState(null); // ID of item to delete

  const fetchExpenses = useCallback(async () => {
    setLoading(true);
    try {
      const params = {};
      if (filterCat !== 'All') params.category = filterCat;
      if (sortOrder === 'date_desc') params.sort = 'date_desc';

      const { data } = await api.get('/expenses', { params });
      setExpenses(data.items || []);
      setServerTotal(data.total || "0");
    } catch (error) {
      console.error("Failed to fetch expenses", error);
      if (error.response?.status !== 401) {
        toast.error("Could not load expenses");
      }
    } finally {
      setLoading(false);
    }
  }, [filterCat, sortOrder]);

  useEffect(() => {
    fetchExpenses();
  }, [fetchExpenses]);

  // Handlers
  const handleOpenCreate = () => {
    setEditingExpense(null);
    setIsFormOpen(true);
  };

  const handleOpenEdit = (expense) => {
    setEditingExpense(expense);
    setIsFormOpen(true);
  };

  const handleFormSuccess = () => {
    setIsFormOpen(false);
    fetchExpenses();
  };

  const confirmDelete = (id) => {
    setDeleteId(id);
  };

  const handleDeleteExecute = async () => {
    try {
      await api.delete(`/expenses/${deleteId}`);
      toast.success("Expense deleted");
      fetchExpenses();
    } catch (error) {
      console.error(error);
      toast.error("Failed to delete expense");
    } finally {
      setDeleteId(null);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      
      {/* 1. Summary Section */}
      <ExpenseSummary expenses={expenses} serverTotal={serverTotal} />

      {/* 2. Controls & Add Button */}
      <div className="flex flex-col sm:flex-row justify-between items-center gap-4 bg-white p-4 rounded-2xl border border-slate-100 shadow-sm">
        <div className="flex items-center gap-3 w-full sm:w-auto">
          {/* Category Filter */}
          <div className="relative group">
            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 group-focus-within:text-primary transition-colors" />
            <select 
              className="pl-9 pr-4 py-2 bg-slate-50 border-none rounded-xl text-sm font-medium text-slate-700 focus:ring-2 focus:ring-primary/20 cursor-pointer hover:bg-slate-100 transition-colors appearance-none"
              value={filterCat}
              onChange={(e) => setFilterCat(e.target.value)}
            >
              {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          
          {/* Sort Button */}
          <button 
            onClick={() => setSortOrder(prev => prev === 'date_desc' ? null : 'date_desc')}
            className={`flex items-center gap-2 text-sm px-4 py-2 rounded-xl transition-all font-medium ${
              sortOrder === 'date_desc' 
                ? 'bg-primary/10 text-primary ring-1 ring-primary/20' 
                : 'bg-slate-50 text-slate-600 hover:bg-slate-100'
            }`}
          >
            <ArrowUpDown className="w-4 h-4" />
            {sortOrder === 'date_desc' ? 'Newest' : 'Oldest'}
          </button>
        </div>

        {/* Create Button */}
        <Button 
          onClick={handleOpenCreate} 
          className="w-full sm:w-auto shadow-lg shadow-primary/25 hover:shadow-primary/40 rounded-xl"
        >
          <Plus className="w-5 h-5 mr-2" /> Add Expense
        </Button>
      </div>

      {/* 3. The List */}
      <ExpenseList 
        expenses={expenses} 
        isLoading={loading} 
        onDelete={confirmDelete}
        onEdit={handleOpenEdit}
      />

      {/* --- MODALS --- */}

      {/* Create / Edit Modal */}
      <Modal
        isOpen={isFormOpen}
        onClose={() => setIsFormOpen(false)}
        title={editingExpense ? "Edit Transaction" : "New Transaction"}
      >
        <ExpenseForm 
          onSuccess={handleFormSuccess} 
          initialData={editingExpense}
          onCancel={() => setIsFormOpen(false)}
          isModal={true}
        />
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={!!deleteId}
        onClose={() => setDeleteId(null)}
        title="Confirm Deletion"
        maxWidth="max-w-sm"
      >
        <div className="text-center space-y-4">
          <div className="w-12 h-12 bg-red-50 text-red-500 rounded-full flex items-center justify-center mx-auto mb-2">
            <Trash2 className="w-6 h-6" />
          </div>
          <p className="text-slate-600">
            Are you sure you want to delete this expense? <br/>
            <span className="text-sm text-slate-400">This action cannot be undone.</span>
          </p>
          <div className="flex gap-3 justify-center mt-6">
            <Button variant="secondary" onClick={() => setDeleteId(null)}>
              Cancel
            </Button>
            <Button variant="danger" onClick={handleDeleteExecute}>
              Delete It
            </Button>
          </div>
        </div>
      </Modal>

    </div>
  );
}