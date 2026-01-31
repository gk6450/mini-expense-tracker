import { useMemo } from 'react';
import { formatCurrency } from '../../utils/format';
import { PieChart } from 'lucide-react';

export default function ExpenseSummary({ expenses, serverTotal }) {
  const stats = useMemo(() => {
    // If serverTotal is provided (string), use it. Otherwise calc from list.
    const total = serverTotal ? parseFloat(serverTotal) : expenses.reduce((acc, curr) => acc + parseFloat(curr.amount), 0);
    
    // We still need to calculate category breakdown from the loaded items
    const byCategory = expenses.reduce((acc, curr) => {
      acc[curr.category] = (acc[curr.category] || 0) + parseFloat(curr.amount);
      return acc;
    }, {});

    return { total, byCategory };
  }, [expenses, serverTotal]);

  return (
    <div className="bg-gradient-to-br from-primary to-emerald-600 text-white p-6 rounded-2xl shadow-lg shadow-primary/20 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-primary-100 font-medium flex items-center gap-2">
          <PieChart className="w-5 h-5" /> Total Spent
        </h2>
      </div>
      
      <div className="text-4xl font-bold mb-6 tracking-tight">
        {formatCurrency(stats.total)}
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        {Object.entries(stats.byCategory).map(([cat, amount]) => (
          <div key={cat} className="bg-white/10 backdrop-blur-sm p-3 rounded-lg border border-white/10">
            <div className="text-xs text-primary-100 mb-1">{cat}</div>
            <div className="font-semibold">{formatCurrency(amount)}</div>
          </div>
        ))}
      </div>
    </div>
  );
}