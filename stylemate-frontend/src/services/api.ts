import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
});

export const wardrobeService = {
  // Upload wardrobe item
  uploadItem: async (
    file: File,
    userId: string,
    enhance = true
  ) => {
    const formData = new FormData();
    formData.append("file", file);

    return api.post(
      `/upload/upload?user_id=${userId}&enhance_with_ai=${enhance}`,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );
  },

  // Get all wardrobe items
  getWardrobe: async (userId: string) => {
    return api.get(`/upload/?user_id=${userId}`);
  },

  // Delete wardrobe item
  deleteWardrobeItem: async (itemId: string) => {
    return api.delete(`/upload/${itemId}`);
  },

  // AI stylist recommendation
  getProRecommendation: async (
    userId: string,
    prompt: string,
    city: string
  ) => {
    return api.post("/recommend/pro", {
      user_id: userId,
      prompt,
      city,
    });
  },

  // Group outfit matching
  matchMultiUser: async (
    userIds: string[],
    context: any
  ) => {
    return api.post("/outfit/match-multi", {
      user_ids: userIds,
      context,
    });
  },
};

export default api;