import { Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogOut, Wallet } from 'lucide-react';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

export default function Layout() {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <nav className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center gap-2">
              <div className="bg-primary/10 p-2 rounded-lg">
                <Wallet className="w-6 h-6 text-primary" />
              </div>
              <span className="font-bold text-xl text-slate-800 tracking-tight">Expense<span className="text-primary">Tracker</span></span>
            </div>
            <div className="flex items-center">
              <button 
                onClick={handleLogout}
                className="text-sm font-medium text-slate-500 hover:text-red-600 flex items-center gap-2 transition-colors"
              >
                <LogOut className="w-4 h-4" /> Sign out
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="flex-1 py-8 px-4 sm:px-6 lg:px-8 max-w-5xl mx-auto w-full">
        <Outlet />
      </main>

      <ToastContainer position="bottom-right" theme="colored" />
    </div>
  );
}