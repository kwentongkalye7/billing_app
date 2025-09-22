import { create } from "zustand";
import { persist } from "zustand/middleware";
import axios from "axios";
import type { User } from "../types/api";

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isLoading: boolean;
  login: (values: { username: string; password: string }) => Promise<void>;
  logout: () => Promise<void>;
  bootstrap: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isLoading: false,
      login: async ({ username, password }) => {
        set({ isLoading: true });
        try {
          const { data } = await axios.post(`/auth/login/`, { username, password }, { baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000/api" });
          set({
            user: data.user,
            accessToken: data.access,
            refreshToken: data.refresh,
            isLoading: false,
          });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },
      logout: async () => {
        const refresh = get().refreshToken;
        try {
          await axios.post(`/auth/logout/`, { refresh }, { baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000/api" });
        } catch (error) {
          console.warn("Logout error", error);
        }
        set({ user: null, accessToken: null, refreshToken: null });
      },
      bootstrap: async () => {
        const token = get().accessToken;
        if (!token) return;
        try {
          const { data } = await axios.get(`/users/me/`, { baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000/api", headers: { Authorization: `Bearer ${token}` } });
          set({ user: data });
        } catch (error) {
          console.warn("Bootstrap session failed", error);
          set({ user: null, accessToken: null, refreshToken: null });
        }
      },
    }),
    {
      name: "billing-auth",
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        user: state.user,
      }),
    }
  )
);
