import { useAuth } from '../../context/AuthContext';
import BuyerDashboard from './BuyerDashboard';
import SellerDashboard from './SellerDashboard';
import AdminDashboardBento from './AdminDashboardBento';

export default function DashboardIndex() {
  const { user } = useAuth();

  if (!user) {
    return <div>Chargement... (Ou redirection vers login)</div>;
  }

  if (user.role === 'admin') {
    return <AdminDashboardBento />;
  }

  if (user.role === 'seller') {
    return <SellerDashboard />;
  }

  // Default to buyer
  return <BuyerDashboard />;
}
