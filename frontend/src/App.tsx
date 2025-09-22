import { useEffect } from "react";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";

import { DashboardLayout } from "./layouts/DashboardLayout";
import { ProtectedRoute } from "./components/ProtectedRoute";
import DashboardPage from "./pages/DashboardPage";
import ClientsPage from "./pages/ClientsPage";
import EngagementsPage from "./pages/EngagementsPage";
import StatementsPage from "./pages/StatementsPage";
import PaymentsPage from "./pages/PaymentsPage";
import ReportsPage from "./pages/ReportsPage";
import LoginPage from "./pages/LoginPage";
import { useAuthStore } from "./hooks/useAuth";

const App = () => {
  const { user, bootstrap } = useAuthStore();
  const location = useLocation();

  useEffect(() => {
    bootstrap();
  }, []);

  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/" replace /> : <LoginPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="clients" element={<ClientsPage />} />
        <Route path="engagements" element={<EngagementsPage />} />
        <Route path="statements" element={<StatementsPage />} />
        <Route path="payments" element={<PaymentsPage />} />
        <Route path="reports" element={<ReportsPage />} />
      </Route>
      <Route path="*" element={<Navigate to={user ? location.pathname : "/login"} replace />} />
    </Routes>
  );
};

export default App;
