import { defineConfig, loadEnv } from "vite";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  return {
    esbuild: {
      jsx: "automatic",
      jsxDev: mode !== "production",
    },
    server: {
      port: Number(env.VITE_PORT ?? 5173),
      host: "0.0.0.0",
    },
    build: {
      outDir: "dist",
      sourcemap: true,
    },
  };
});
