import api from "./api";

let creatorsCache = null;
const creatorBySlugCache = new Map();

export const creatorService = {
  /**
   * Fetch all creators.
   * @param {boolean} forceRefresh Whether to bypass the cache and fetch fresh data.
   * @returns {Promise<Array<any>>} Resolves with a list of all creators.
   *
   * @throws {string} Throws an error message if the request fails.
   */
  getAllCreators: async (forceRefresh = false) => {
    try {
      if (creatorsCache && !forceRefresh) {
        return creatorsCache;
      }
      const response = await api.get("/creators/all/");
      creatorsCache = response.data;

      // Populate individual cache for faster profile loading
      const creators = Array.isArray(creatorsCache)
        ? creatorsCache
        : creatorsCache?.data;

      if (Array.isArray(creators)) {
        creators.forEach((c) => {
          const slug = c.user?.slug || c.slug;
          if (slug) creatorBySlugCache.set(slug, c);
        });
      }

      return creatorsCache;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  /**
   * Fetch a single creator by their URL slug.
   * @param {string} slug The unique URL-friendly identifier of the creator.
   * @param {boolean} forceRefresh Whether to bypass the cache and fetch fresh data.
   *
   * @returns {Promise<any>}  Resolves with the creator object.
   *
   * @throws {string} Throws an error message if the creator cannot be retrieved.
   */
  getCreatorBySlug: async (slug, forceRefresh = false) => {
    try {
      if (creatorBySlugCache.has(slug) && !forceRefresh) {
        return creatorBySlugCache.get(slug);
      }
      const response = await api.get(`/creators/${slug}/`);
      creatorBySlugCache.set(slug, response.data);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message || "Failed to fetch creator.";
    }
  },

  /**
   * Fully updates (replaces) the authenticated creator’s profile.
   * @param {{
   *   firstName: string,
   *   lastName: string,
   *   bio: string,
   *   profileImage: string,
   *   coverImage: string
   * }} userData The complete creator profile payload.
   *
   * @returns {Promise<{
   *   success: boolean,
   *   data?: any,
   *   error?: string
   * }>} Returns a success flag and updated creator data,
   *  or an error message if the update fails.
   */
  updateCreator: async (userData) => {
    try {
      const response = await api.putForm("/creators/profile/me/", userData);

      return {
        success: true,
        data: response.data?.data || response.data,
      };
    } catch (error) {
      return {
        success: false,
        error:
          error.response?.data?.message ||
          error.response?.data?.error ||
          "Update failed",
      };
    }
  },
};

