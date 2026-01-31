import { motion, AnimatePresence } from 'framer-motion';
import { formatCurrency, formatDateOnly } from '../../utils/format';
import { Tag, Calendar, Pencil, Trash2, Loader2 } from 'lucide-react';

export default function ExpenseList({ expenses, isLoading, onDelete, onEdit }) {
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 bg-white/50 rounded-2xl border border-dashed border-slate-200">
        <Loader2 className="w-10 h-10 text-primary animate-spin mb-3" />
        <p className="text-slate-400 font-medium">Loading transactions...</p>
      </div>
    );
  }

  if (expenses.length === 0) {
    return (
      <div className="text-center py-20 bg-white rounded-2xl border border-dashed border-slate-200">
        <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-4">
          <Tag className="w-6 h-6 text-slate-300" />
        </div>
        <p className="text-slate-500 font-medium">No expenses found.</p>
        <p className="text-slate-400 text-sm mt-1">Add a new transaction to get started.</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <AnimatePresence>
        {expenses.map((expense) => (
          <motion.div
            key={expense.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="group bg-white p-5 rounded-2xl border border-slate-100 shadow-sm hover:shadow-md transition-all hover:border-primary/20"
          >
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
              
              {/* Left Side: Icon & Info */}
              <div className="flex items-start gap-4 flex-1">
                {/* Category Icon Placeholder */}
                <div className="w-10 h-10 rounded-xl bg-slate-50 text-slate-500 flex items-center justify-center flex-shrink-0 group-hover:bg-primary/10 group-hover:text-primary transition-colors">
                  <Tag className="w-5 h-5" />
                </div>

                <div>
                  <h4 className="font-semibold text-slate-800 text-base">{expense.description || 'Untitled Expense'}</h4>
                  <div className="flex items-center gap-3 mt-1 text-sm text-slate-400">
                    <span className="flex items-center gap-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-slate-300"></span>
                      {expense.category}
                    </span>
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3 h-3" />
                      {formatDateOnly(expense.date)}
                    </span>
                  </div>
                </div>
              </div>
              
              {/* Right Side: Amount & Actions */}
              <div className="flex items-center gap-6 w-full sm:w-auto justify-between sm:justify-end mt-2 sm:mt-0 pl-14 sm:pl-0">
                <span className="text-lg font-bold text-slate-900 tracking-tight">
                  {formatCurrency(expense.amount)}
                </span>
                
                {/* Action Buttons */}
                <div className="flex items-center gap-1">
                  <button 
                    onClick={() => onEdit(expense)}
                    className="p-2 text-slate-400 hover:text-primary hover:bg-primary/5 rounded-lg transition-colors"
                    title="Edit"
                  >
                    <Pencil className="w-4 h-4" />
                  </button>
                  <button 
                    onClick={() => onDelete(expense.id)}
                    className="p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                    title="Delete"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}