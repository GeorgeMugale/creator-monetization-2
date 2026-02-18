import { useState, useEffect } from "react";
import {
  Wallet,
  ArrowUpRight,
  TrendingUp,
  Calendar,
  Clock,
  AlertCircle,
} from "lucide-react";
import { walletService } from "../../services/walletService";

// Skeleton Primitives
const Shimmer = ({ className = "" }) => (
  <div
    className={`animate-pulse bg-gradient-to-r from-gray-100 via-gray-200 to-gray-100 bg-[length:400%_100%] rounded-lg ${className}`}
    style={{
      animation: "shimmer 1.6s ease-in-out infinite",
    }}
  />
);

const ShimmerStyles = () => (
  <style>{`
    @keyframes shimmer {
      0%   { background-position: 100% 50%; }
      100% { background-position: 0%   50%; }
    }
  `}</style>
);

const StatCardSkeleton = () => (
  <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
    <div className="flex items-center gap-3 mb-4">
      <Shimmer className="w-12 h-12 rounded-xl" />
      <Shimmer className="h-4 w-32" />
    </div>
    <Shimmer className="h-9 w-40 mt-1" />
  </div>
);

const PayoutInfoSkeleton = () => (
  <div className="grid grid-cols-1 md:grid-cols-3 gap-6 bg-gray-50 rounded-xl p-6 border border-gray-100">
    {[0, 1, 2].map((i) => (
      <div key={i}>
        <Shimmer className="h-3.5 w-24 mb-3" />
        <Shimmer className="h-7 w-36" />
      </div>
    ))}
  </div>
);

const FundsAndPayouts = ({ walletData, loading }) => {
  const [hasPayoutData, setHasPayoutData] = useState(true);
  const [data, setData] = useState(null);
  const [innerLoading, setInnerLoading] = useState(false);
  const [payoutError, setPayoutError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setInnerLoading(true);
      try {
        const response = await walletService.getPayoutsData();
        if (response) {
          setData(response);
          setHasPayoutData(true);
        }
      } catch (err) {
        console.error(err);
        setPayoutError(err?.response?.data?.message || "Failed to load payout schedule.");
      } finally {
        setInnerLoading(false);
      }
    };

    fetchData();
  }, []);

  const isLoading = loading || innerLoading;

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <ShimmerStyles />
      <div className="max-w-5xl mx-auto space-y-8">
        {/* Page Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Funds & Payouts</h1>
          <p className="text-gray-500 mt-1">
            Manage your earnings, balances, and withdrawal schedule.
          </p>
        </div>

        {/* ── Stat Cards ── */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {isLoading ? (
            <>
              <StatCardSkeleton />
              <StatCardSkeleton />
              <StatCardSkeleton />
            </>
          ) : walletData ? (
            <>
              {/* Available Balance */}
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-3 bg-green-50 rounded-xl text-green-600">
                    <Wallet size={24} />
                  </div>
                  <h2 className="text-sm font-bold text-gray-600">Available Balance</h2>
                </div>
                <p className="text-3xl font-black text-gray-900">
                  {walletData.balance}{" "}
                  <span className="text-lg font-semibold text-gray-400">
                    {walletData.currency}
                  </span>
                </p>
              </div>
              
              {/* Total Paid Out */}
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-3 bg-orange-50 text-orange-600 rounded-xl">
                    <ArrowUpRight size={24} />
                  </div>
                  <h2 className="text-sm font-bold text-gray-600">Total Paid Out</h2>
                </div>
                <p className="text-3xl font-black text-gray-900">
                  {walletData.cashOut}{" "}
                  <span className="text-lg font-semibold text-gray-400">
                    {walletData.currency}
                  </span>
                </p>
              </div>
              
              {/* Lifetime Earnings */}
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-3 bg-blue-50 rounded-xl text-blue-600">
                    <TrendingUp size={24} />
                  </div>
                  <h2 className="text-sm font-bold text-gray-600">Lifetime Earnings</h2>
                </div>
                <p className="text-3xl font-black text-gray-900">
                  {walletData.cashIn}{" "}
                  <span className="text-lg font-semibold text-gray-400">
                    {walletData.currency}
                  </span>
                </p>
              </div>
            </>
          ) : (
            // Fallback if walletData is missing entirely
            <div className="col-span-1 md:col-span-3 bg-white p-6 rounded-2xl border border-gray-100 text-center text-gray-500">
              Wallet data is currently unavailable.
            </div>
          )}
        </div>

        {/*Next Payout + Withdraw*/}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="p-6 md:p-8 border-b border-gray-100">
            <h2 className="text-lg font-bold text-gray-900 mb-6 flex items-center gap-2">
              <Calendar size={20} className="text-gray-400" />
              Next Payout Information
            </h2>

            {isLoading ? (
              <PayoutInfoSkeleton />
            ) : payoutError ? (
              /* Localized Error State for Payouts */
              <div className="flex items-center justify-between bg-red-50 text-red-600 rounded-xl p-6 border border-red-100">
                <div className="flex items-center gap-3">
                  <AlertCircle size={24} />
                  <p className="font-medium">{payoutError}</p>
                </div>
                <button 
                  onClick={() => window.location.reload()} 
                  className="px-4 py-2 bg-red-600 text-white text-sm font-bold rounded-lg hover:bg-red-700 transition-colors"
                >
                  Retry
                </button>
              </div>
            ) : hasPayoutData && data ? (
              /* Active State */
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 bg-gray-50 rounded-xl p-6 border border-gray-100">
                <div>
                  <p className="text-sm text-gray-500 mb-1 font-medium">Estimated Amount</p>
                  <p className="text-2xl font-bold text-green-600">
                    {/* CRITICAL FIX: Added optional chaining to walletData?.currency */}
                    {data.estimatedAmount} {walletData?.currency || ""}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500 mb-1 font-medium flex items-center gap-1.5">
                    <Calendar size={14} /> Payout Date
                  </p>
                  <p className="text-lg font-bold text-gray-900">{data.date}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500 mb-1 font-medium flex items-center gap-1.5">
                    <Clock size={14} /> Schedule
                  </p>
                  <p className="text-lg font-bold text-gray-900">{data.schedule}</p>
                </div>
              </div>
            ) : (
              /* Empty State */
              <div className="flex flex-col items-center justify-center py-10 px-4 bg-gray-50 rounded-xl border border-dashed border-gray-200 text-center">
                <div className="p-3 bg-white rounded-full shadow-sm border border-gray-100 mb-4">
                  <AlertCircle size={24} className="text-gray-400" />
                </div>
                <p className="text-gray-900 font-bold mb-1">No active payout schedule</p>
                <p className="text-sm text-gray-500 max-w-sm">
                  Next payout date will appear here once withdrawals are enabled.
                </p>
              </div>
            )}
          </div>

          {/* Withdraw Button */}
          <div className="p-6 md:p-8 bg-gray-50/50 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
            <div className="flex-1">
              {isLoading ? (
                <Shimmer className="h-4 w-72" />
              ) : (
                <p className="text-sm text-gray-500 font-medium">
                  Withdrawals will be available soon. You'll see your payout schedule above once activated.
                </p>
              )}
            </div>

            {isLoading ? (
              <Shimmer className="w-full md:w-48 h-12 rounded-xl" />
            ) : (
              <button
                disabled
                className="w-full md:w-auto px-8 py-3.5 bg-gray-900 text-white font-bold rounded-xl opacity-40 cursor-not-allowed flex items-center justify-center gap-2 transition-all"
              >
                <Wallet size={18} />
                Withdraw (Coming Soon)
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default FundsAndPayouts;