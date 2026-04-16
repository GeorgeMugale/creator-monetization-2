import axios from "axios";
import { auth } from "../firebase";

// Setup Constants (Fixed for Vite)
const BASE_URL = import.meta.env.VITE_API_URL || "";
const TIMEOUT = Number(import.meta.env.VITE_API_TIMEOUT) || 30000;
const API_KEY = import.meta.env.VITE_API_CLIENT_KEY || "";

// Create Axios Instance
const api = axios.create({
  baseURL: BASE_URL,
  timeout: TIMEOUT,
  headers: {
    Accept: "application/json",
    "X-API-KEY": API_KEY,
  },
});

// Request Interceptor (Attach Firebase Token)
api.interceptors.request.use(
  async (config) => {
    const user = auth.currentUser;

    if (user) {
      try {
        // Force refresh if token is expired or close to expiring
        const token = await user.getIdToken();
        config.headers.Authorization = `Bearer ${token}`;
      } catch (error) {
        console.error("Error getting Firebase ID token:", error);
      }
    }
    
    return config;
  },
  (error) => Promise.reject(error),
);

// Response Interceptor (Handle 401)
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    // If error is 401 (Unauthorized), it might mean the token is invalid or user is not logged in
    if (error.response?.status === 401) {
      try {
        await auth.signOut();
      } catch (signOutError) {
        console.error("Error signing out after 401:", signOutError);
      }
      
      // Clear any remaining local storage and redirect
      localStorage.clear();
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }

    return Promise.reject(error);
  },
);

export default api;
