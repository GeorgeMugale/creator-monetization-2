import api from "./api";

export const creatorService = {
  // Fetch all creators for the catalog page
  getAllCreators: async () => {
    try {
      const response = await api.get("/creators/all/");
      return response.data; // Expecting { status: "success", data: [...] }
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Fetch a single creator by their URL slug
  getCreatorBySlug: async (slug) => {
    try {
      const response = await api.get(`/creators/${slug}/`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  updateCreator: async (userData) => {
    console.log(userData);
    try {
      const response = await api.put("/creators/profile/me", userData);

      return { success: true, data: response.data };
    } catch (error) {
      return {
        success: false,
        error:
          error.response?.data?.message ||
          error.response?.data?.error ||
          "Profile update failed. Please try again.",
      };
    }
  },
};
