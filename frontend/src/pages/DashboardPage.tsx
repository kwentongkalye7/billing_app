import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { axiosClient } from "../api/client";
import { PageHeader } from "../components/PageHeader";
import type { BillingStatement, Payment } from "../types/api";

const DashboardPage = () => {
  const { data: statements } = useQuery<BillingStatement[]>({
    queryKey: ["statements", { limit: 5 }],
    queryFn: async () => {
      const { data } = await axiosClient.get<BillingStatement[]>("/billing-statements/?ordering=-updated_at&limit=5");
      return data;
    },
  });

  const { data: payments } = useQuery<Payment[]>({
    queryKey: ["payments", { limit: 5 }],
    queryFn: async () => {
      const { data } = await axiosClient.get<Payment[]>("/payments/?ordering=-payment_date&limit=5");
      return data;
    },
  });

  return (
    <div className="space-y-6">
      <PageHeader
        title="Dashboard"
        description="At-a-glance view of recent activity across statements and collections."
      />
      <div className="grid gap-4 md:grid-cols-2">
        <section className="rounded-xl border border-slate-200 bg-white p-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-slate-700">Recently Issued Statements</h3>
            <Link to="/statements" className="text-xs text-primary hover:underline">
              View all
            </Link>
          </div>
          <ul className="mt-3 space-y-2 text-sm">
            {statements?.length ? (
              statements.map((stmt) => (
                <li key={stmt.id} className="flex items-center justify-between rounded-md bg-slate-50 px-3 py-2">
                  <div>
                    <div className="font-medium">{stmt.number ?? "Draft"}</div>
                    <div className="text-xs text-slate-500">{stmt.client_name} • {stmt.period}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs uppercase text-slate-500">Balance</div>
                    <div className="font-semibold">₱{Number(stmt.balance).toLocaleString()}</div>
                  </div>
                </li>
              ))
            ) : (
              <li className="rounded-md bg-slate-50 px-3 py-6 text-center text-xs text-slate-500">
                No statements yet. Start by creating a retainer run or special engagement.
              </li>
            )}
          </ul>
        </section>
        <section className="rounded-xl border border-slate-200 bg-white p-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-slate-700">Recent Payments</h3>
            <Link to="/payments" className="text-xs text-primary hover:underline">
              View all
            </Link>
          </div>
          <ul className="mt-3 space-y-2 text-sm">
            {payments?.length ? (
              payments.map((payment) => (
                <li key={payment.id} className="flex items-center justify-between rounded-md bg-slate-50 px-3 py-2">
                  <div>
                    <div className="font-medium">₱{Number(payment.amount_received).toLocaleString()}</div>
                    <div className="text-xs text-slate-500">
                      {payment.client_name} • {payment.payment_date}
                    </div>
                  </div>
                  <div className="text-right text-xs text-slate-500">
                    Method: {payment.method.replace("_", " ")}
                    <br />
                    Remaining: ₱{Number(payment.remaining_unallocated).toLocaleString()}
                  </div>
                </li>
              ))
            ) : (
              <li className="rounded-md bg-slate-50 px-3 py-6 text-center text-xs text-slate-500">
                No payments recorded yet. Use the Payments screen to log settlements and allocations.
              </li>
            )}
          </ul>
        </section>
      </div>
    </div>
  );
};

export default DashboardPage;
