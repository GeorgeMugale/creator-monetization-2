import api from './api';

export const getWalletData = async (page = {page: 1, limit: 10}) => {
  await new Promise(resolve => setTimeout(resolve, 1000));
  try {
    const response = await api.get(`/wallets/me?page=${page}`);
    return response.data.data; 
  } catch (error) {
    throw error.response?.data || { message: "Failed to fetch wallet data" };
  }
};


export const getWalletTxnData = async (page = {page: 1, limit: 10}) => {
  await new Promise(resolve => setTimeout(resolve, 1000));
  try {
    const response = await api.get(`/wallets/transactions?page=${page}`);
    return response.data.data; 
  } catch (error) {
    throw error.response?.data || { message: "Failed to fetch wallet transactions data" };
  }
};
