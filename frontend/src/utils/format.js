import { format, parseISO } from 'date-fns';

export const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 2
  }).format(amount);
};

export const formatDate = (dateString) => {
  if (!dateString) return '';
  return format(parseISO(dateString), 'MMM d, yyyy h:mm a');
};

export const formatDateOnly = (dateString) => {
  if (!dateString) return '';
  return format(parseISO(dateString), 'MMM d, yyyy');
};