import api from "./api";

export const authService = {
  // Log in a user
  loginUser: async (email, password) => {
    try {
      const response = await api.post("/auth/token/", {
        email,
        password,
      });

      // Return the backend's response data
      return { success: true, data: response.data };
    } catch (error) {
      console.error("Login API Error:", error.response);
      return {
        success: false,
        error:
          error.response?.data?.message ||
          "Login failed. Please check your connection.",
      };
    }
  },

  // Register a User
  registerUser: async (userData) => {
    try {
      const response = await api.post("/auth/register/", userData);

      return { success: true, data: response.data };
    } catch (error) {
      console.error("Register API Error:", error.response);
      return {
        success: false,
        error:
          error.response?.data?.message ||
          "Registration failed. Please try again.",
      };
    }
  },

  logoutUser: async () => {
    try {
      const response = await api.post("/auth/logout/");

      return { success: true, data: response.data };
    } catch (error) {
      console.error("Logout API Error:", error.response);
      return {
        success: false,
        error:
          error.response?.data?.message || "Logout failed. Please try again.",
      };
    }
  },

  getProfile: async () => {
    try {
      const response = await api.get("/auth/profile/");

      return { success: true, data: response.data };
    } catch (error) {
      console.error("Logout API Error:", error.response);
      return {
        success: false,
        error:
          error.response?.data?.message || "Logout failed. Please try again.",
      };
    }
  },

};

