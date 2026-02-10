import api from "./api";

export const walletService = {
  getWalletData: async (page = 1) => {
    await new Promise((resolve) => setTimeout(resolve, 1000));
    try {
      const response = await api.get(`/wallets/me?page=${page}`);
      return response.data.data;
    } catch (error) {
      throw error.response?.data || { message: "Failed to fetch wallet data" };
    }
  },

  getWalletTxnData: async (page = 1) => {
    await new Promise((resolve) => setTimeout(resolve, 1000));
    try {
      const response = await api.get(`/wallets/transactions?page=${page}`);
      return response.data;
    } catch (error) {
      throw (
        error.response?.data || {
          message: "Failed to fetch wallet transactions data",
        }
      );
    }
  },
};
