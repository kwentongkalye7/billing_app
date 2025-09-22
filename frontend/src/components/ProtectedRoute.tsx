import { Navigate } from "react-router-dom";

import { useAuthStore } from "../hooks/useAuth";

interface Props {
  children: JSX.Element;
  roles?: Array<"admin" | "biller" | "reviewer" | "viewer">;
}

export const ProtectedRoute = ({ children, roles }: Props) => {
  const { user } = useAuthStore();
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  if (roles && !roles.includes(user.role)) {
    return <Navigate to="/" replace />;
  }
  return children;
};
