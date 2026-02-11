import {
  Inbox,
} from "lucide-react";

const Transactions = ({ txnData, isTransactionsView, error, setPage, loading, walletData, page }) => {
  return (
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
            ) : txnData?.data.length > 0 ? (
              txnData?.data.map((txn) => (
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
                    {walletData.currency} {Number(txn.amount).toFixed(2)}
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
      {isTransactionsView && txnData?.count > 1 && (
        <div className="p-6 bg-gray-50 border-t border-gray-100 flex justify-between items-center">
          <button
            disabled={page === 1}
            onClick={() => setPage((p) => p - 1)}
            className="text-xs font-bold disabled:opacity-30"
          >
            Prev
          </button>
          <span className="text-xs font-bold">
            Page {page} of {txnData?.count}
          </span>
          <button
            disabled={page >= txnData?.count}
            onClick={() => setPage((p) => p + 1)}
            className="text-xs font-bold disabled:opacity-30"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
};

const LoaderSpin = () => (
  <div className="flex items-center text-xs font-bold text-gray-400 animate-pulse">
    <div className="animate-spin mr-2 h-3 w-3 border-2 border-zed-green border-t-transparent rounded-full"></div>
    Updating...
  </div>
);

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

export default Transactions;
