import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, ArrowRightLeft, X } from 'lucide-react';

const Sidebar = ({ onClose, isMobile = false, showCloseButton = false, title='' }) => {
  const location = useLocation();

  const menuItems = [
    { icon: LayoutDashboard, label: 'Overview', path: '/dashboard' },
    { icon: ArrowRightLeft, label: 'Transactions', path: '/dashboard/transactions' },
  ];

  const handleLinkClick = () => {
    // Close mobile menu when a link is clicked
    if (isMobile && onClose) {
      onClose();
    }
  };

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Mobile Header with Close Button (only visible on mobile when sidebar is open) */}
      {showCloseButton && (
        <div className="md:hidden p-4 border-b border-gray-200 flex justify-between items-center">
          <span className="text-xl font-bold text-green-600">{title}</span>
          <button 
            onClick={onClose} 
            className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            aria-label="Close menu"
          >
            <X size={24} />
          </button>
        </div>
      )}

      {/* Desktop Header (only visible on desktop) */}
      <div className="hidden md:block p-6 border-b border-gray-200">
        <span className="text-xl font-bold text-green-600">{title}</span>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-4 py-4 space-y-2">
        {menuItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              onClick={handleLinkClick}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                isActive 
                  ? 'bg-green-50 text-green-600' 
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              <item.icon size={20} />
              {item.label}
            </Link>
          );
        })}
      </nav>

  
    </div>
  );
};

export default Sidebar;