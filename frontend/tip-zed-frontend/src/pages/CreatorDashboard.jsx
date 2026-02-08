import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import DashboardLayout from "@/layouts/DashboardLayout";
import { useAuth } from "@/hooks/useAuth";
import { walletService } from "@/services/walletService";
import {
  TrendingUp,
  DollarSign,
  ArrowUpRight,
  Inbox,
  ShieldCheck,
  ArrowDownLeft,
  AlertCircle
} from "lucide-react";

const CreatorDashboard = () => {
  const { user } = useAuth();
  const { pathname } = useLocation();

  // determine which "mode" the page is in
  const isTransactionsView = pathname === "/creator-dashboard/transactions";

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // If it's overview, we always want page 1. If it's txn view, use current page state.
        const currentPage = isTransactionsView ? page : 1;
        const responseWallet = await walletService.getWalletData(currentPage);
        setData(responseWallet);
      } catch (err) {
        setError(err?.response?.data?.message || "Failed to load data.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [page, isTransactionsView]);

  if (loading && !data) {
    return (
      <DashboardLayout title={user?.username}>
        <div className="animate-pulse space-y-8">
          <div className="h-8 bg-gray-200 w-1/4 rounded-lg"></div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="h-32 bg-gray-100 rounded-2xl"></div>
            <div className="h-32 bg-gray-100 rounded-2xl"></div>
            <div className="h-32 bg-gray-100 rounded-2xl"></div>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (error && !data) {
    return (
      <DashboardLayout title={user?.username ?? "Dashboard"}>
        <div className="flex flex-col items-center justify-center py-24 text-center">
          <div className="bg-red-50 border border-red-100 text-red-600 rounded-2xl p-8 max-w-md">
            <AlertCircle size={40} className="mx-auto mb-4" />
            <h2 className="font-black text-lg mb-2">Something went wrong</h2>
            <p className="text-sm font-medium mb-6">{error}</p>

            <button
              onClick={() => window.location.reload()}
              className="bg-red-600 text-white px-5 py-2 rounded-xl text-sm font-bold hover:opacity-90"
            >
              Retry
            </button>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  const statCards = [
    {
      label: "Balance",
      val: data?.balance,
      icon: DollarSign,
      color: "text-zed-green",
      bg: "bg-green-50",
    },
    {
      label: "Incoming",
      val: data?.totalIncoming,
      icon: TrendingUp,
      color: "text-blue-600",
      bg: "bg-blue-50",
    },
    {
      label: "Outgoing",
      val: data?.totalOutgoing,
      icon: ArrowDownLeft,
      color: "text-orange-600",
      bg: "bg-orange-50",
    },
  ];

  return (
    <DashboardLayout title={user?.username ?? "Dashboard"}>
      {/* HEADER SECTION */}
      <div className="mb-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-black text-gray-900 tracking-tight">
            {isTransactionsView ? "Transaction History" : "Overview"}
          </h1>
          <div className="flex items-center gap-2 mt-1">
            <span className="bg-gray-100 text-gray-500 px-2 py-0.5 rounded text-[10px] font-bold uppercase">
              {data?.kycLevel}
            </span>
            {data?.kycVerified && (
              <ShieldCheck size={14} className="text-zed-green" />
            )}
          </div>
        </div>

        {!isTransactionsView && (
          <button className="bg-zed-green text-white px-6 py-3 rounded-xl font-bold shadow-lg flex items-center gap-2 hover:scale-105 transition-all text-sm">
            Withdraw Funds <ArrowUpRight size={18} />
          </button>
        )}
      </div>

      {error && (
        <div className="mb-6 rounded-xl border border-red-100 bg-red-50 px-6 py-4 text-sm font-bold text-red-600 flex items-center gap-3">
          <AlertCircle size={18} />
          {error}
        </div>
      )}

      {/* STAT CARDS - Only show on Overview */}
      {!isTransactionsView && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
          {statCards.map((stat, i) => (
            <div
              key={i}
              className="bg-white p-6 rounded-[2rem] border border-gray-100 shadow-sm"
            >
              <div
                className={`${stat.bg} ${stat.color} w-10 h-10 flex items-center justify-center rounded-xl mb-4`}
              >
                <stat.icon size={20} />
              </div>
              <p className="text-xs font-bold text-gray-400 uppercase">
                {stat.label}
              </p>
              <h3 className="text-2xl font-black text-gray-900">
                {data?.currency} {Number(stat.val).toLocaleString()}
              </h3>
            </div>
          ))}
        </div>
      )}

      {/* TRANSACTIONS SECTION */}
      <div className="bg-white rounded-[2rem] border border-gray-100 shadow-sm overflow-hidden">
        <div className="p-8 border-b border-gray-50 flex justify-between items-center">
          <h2 className="text-xl font-black text-gray-900">
            {isTransactionsView ? "Full Statement" : "Recent Activity"}
          </h2>
          {isTransactionsView && loading && <LoaderSpin />}
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="bg-gray-50/50">
                <th className="px-8 py-4 text-[10px] font-black text-gray-400 uppercase">
                  Date
                </th>
                <th className="px-8 py-4 text-[10px] font-black text-gray-400 uppercase">
                  Status
                </th>
                <th className="px-8 py-4 text-[10px] font-black text-gray-400 uppercase">
                  Amount
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {error ? (
                <tr>
                  <td
                    colSpan="4"
                    className="py-16 text-center text-red-500 font-bold"
                  >
                    Failed to load transactions
                  </td>
                </tr>
              ) : data?.recentTransactions?.length > 0 ? (
                data.recentTransactions.map((txn) => (
                  <tr
                    key={txn.id}
                    className="hover:bg-gray-50/50 transition-colors"
                  >
                    <td className="px-8 py-5 text-sm font-bold text-gray-600">
                      {new Date(txn.createdAt).toLocaleDateString("en-GB")}
                    </td>
                    <td className="px-8 py-5">
                      <StatusBadge status={txn.status} />
                    </td>
                    <td className="px-8 py-5 text-sm font-black text-gray-900">
                      {data.currency} {Number(txn.amount).toFixed(2)}
                    </td>
                  </tr>
                ))
              ) : (
                <EmptyState />
              )}
            </tbody>
          </table>
        </div>

        {/* PAGINATION - Only show on Transactions View */}
        {isTransactionsView && data?.pagination?.pages > 1 && (
          <div className="p-6 bg-gray-50 border-t border-gray-100 flex justify-between items-center">
            <button
              disabled={page === 1}
              onClick={() => setPage((p) => p - 1)}
              className="text-xs font-bold disabled:opacity-30"
            >
              Prev
            </button>
            <span className="text-xs font-bold">
              Page {page} of {data.pagination.pages}
            </span>
            <button
              disabled={page >= data.pagination.pages}
              onClick={() => setPage((p) => p + 1)}
              className="text-xs font-bold disabled:opacity-30"
            >
              Next
            </button>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

// Sub-components to keep the main code clean
const StatusBadge = ({ status }) => {
  const styles = {
    completed: "bg-green-50 text-green-600 border-green-100",
    pending: "bg-yellow-50 text-yellow-600 border-yellow-100",
    failed: "bg-red-50 text-red-600 border-red-100",
  };
  return (
    <span
      className={`px-3 py-1 rounded-lg text-[10px] font-black uppercase tracking-tighter border ${styles[status] || styles.pending}`}
    >
      {status}
    </span>
  );
};

const EmptyState = () => (
  <tr>
    <td colSpan="4" className="py-20 text-center">
      <Inbox className="mx-auto text-gray-200 mb-4" size={48} strokeWidth={1} />
      <p className="text-gray-400 font-bold uppercase text-xs tracking-widest">
        No transactions yet
      </p>
    </td>
  </tr>
);

const LoaderSpin = () => (
  <div className="flex items-center text-xs font-bold text-gray-400 animate-pulse">
    <div className="animate-spin mr-2 h-3 w-3 border-2 border-zed-green border-t-transparent rounded-full"></div>
    Updating...
  </div>
);

export default CreatorDashboard;
