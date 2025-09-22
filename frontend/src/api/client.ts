import axios from "axios";

const baseURL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api";

const getTokenFromStorage = () => {
  try {
    const raw = localStorage.getItem("billing-auth");
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    return parsed?.state?.accessToken ?? null;
  } catch (error) {
    console.warn("Failed to parse auth token", error);
    return null;
  }
};

export const axiosClient = axios.create({
  baseURL,
  withCredentials: false,
});

axiosClient.interceptors.request.use((config) => {
  const token = getTokenFromStorage();
  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

axiosClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Soft logout by clearing persisted state
      localStorage.removeItem("billing-auth");
    }
    return Promise.reject(error);
  }
);
