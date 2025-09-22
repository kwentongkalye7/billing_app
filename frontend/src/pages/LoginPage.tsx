import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";

import { useAuthStore } from "../hooks/useAuth";

interface FormValues {
  username: string;
  password: string;
}

const LoginPage = () => {
  const navigate = useNavigate();
  const { register, handleSubmit, formState } = useForm<FormValues>({
    defaultValues: { username: "", password: "" },
  });
  const { login, isLoading } = useAuthStore();
  const onSubmit = async (values: FormValues) => {
    try {
      await login(values);
      navigate("/");
    } catch (error) {
      alert("Login failed. Please check your credentials or contact your admin.");
      console.error(error);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-100 px-4">
      <div className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
        <h1 className="text-2xl font-semibold">Welcome back</h1>
        <p className="mt-2 text-sm text-slate-500">
          Sign in with your billing account credentials. Need help? See the README onboarding steps.
        </p>
        <form onSubmit={handleSubmit(onSubmit)} className="mt-6 space-y-4">
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-slate-700">
              Username
            </label>
            <input
              id="username"
              autoComplete="username"
              className="mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-primary focus:ring-primary"
              placeholder="e.g. admin"
              {...register("username", { required: "Username is required" })}
            />
            {formState.errors.username && (
              <p className="mt-1 text-sm text-red-600">{formState.errors.username.message}</p>
            )}
          </div>
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-slate-700">
              Password
            </label>
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              className="mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-primary focus:ring-primary"
              placeholder="••••••••"
              {...register("password", { required: "Password is required" })}
            />
            {formState.errors.password && (
              <p className="mt-1 text-sm text-red-600">{formState.errors.password.message}</p>
            )}
          </div>
          <button
            type="submit"
            disabled={isLoading}
            className="w-full rounded-md bg-primary px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-primary/90"
          >
            {isLoading ? "Signing in…" : "Sign in"}
          </button>
        </form>
        <div className="mt-4 rounded-md bg-slate-100 p-3 text-xs text-slate-600">
          Tip: Admins can create new users and reset passwords via the Django admin at <code>/admin</code>.
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
