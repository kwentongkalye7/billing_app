import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";

import { axiosClient } from "../api/client";
import { PageHeader } from "../components/PageHeader";
import type { BillingStatement, Client, Payment } from "../types/api";

interface PaymentForm {
  client: number;
  payment_date: string;
  amount_received: number;
  method: string;
  manual_invoice_no: string;
  reference_no?: string;
  note?: string;
  statement?: number;
  allocation_amount?: number;
}

const paymentMethods = [
  { value: "cash", label: "Cash" },
  { value: "check", label: "Check" },
  { value: "bpi_transfer", label: "BPI Bank Transfer" },
  { value: "bdo_transfer", label: "BDO Bank Transfer" },
  { value: "lbp_transfer", label: "LBP Bank Transfer" },
  { value: "gcash", label: "GCash" },
];

const PaymentsPage = () => {
  const queryClient = useQueryClient();
  const { data: clients } = useQuery<Client[]>({
    queryKey: ["clients"],
    queryFn: async () => {
      const { data } = await axiosClient.get<Client[]>("/clients/");
      return data;
    },
  });

  const { data: statements } = useQuery<BillingStatement[]>({
    queryKey: ["statements", { status: "issued" }],
    queryFn: async () => {
      const { data } = await axiosClient.get<BillingStatement[]>("/billing-statements/?status=issued");
      return data;
    },
  });

  const { data: payments } = useQuery<Payment[]>({
    queryKey: ["payments"],
    queryFn: async () => {
      const { data } = await axiosClient.get<Payment[]>("/payments/?ordering=-payment_date");
      return data;
    },
  });

  const form = useForm<PaymentForm>({
    defaultValues: {
      payment_date: new Date().toISOString().slice(0, 10),
      method: "cash",
    },
  });

  const createPayment = useMutation({
    mutationFn: async (values: PaymentForm) => {
      const payload: any = {
        client: values.client,
        payment_date: values.payment_date,
        amount_received: values.amount_received,
        method: values.method,
        manual_invoice_no: values.manual_invoice_no,
        reference_no: values.reference_no,
        notes: values.note,
        allocations: [],
      };
      if (values.statement && values.allocation_amount) {
        payload.allocations.push({
          billing_statement: values.statement,
          amount_applied: values.allocation_amount,
        });
      }
      return axiosClient.post("/payments/", payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["payments"] });
      queryClient.invalidateQueries({ queryKey: ["statements"] });
      form.reset();
    },
  });

  const verifyPayment = useMutation({
    mutationFn: (paymentId: number) => axiosClient.post(`/payments/${paymentId}/verify/`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["payments"] }),
  });

  return (
    <div className="space-y-6">
      <PageHeader
        title="Payments"
        description="Record settlements, enforce manual allocation, and track unapplied credits."
        actions={
          <button
            onClick={form.handleSubmit((values) => createPayment.mutate(values))}
            disabled={createPayment.isLoading}
            className="rounded-md bg-primary px-4 py-2 text-sm font-semibold text-white"
          >
            {createPayment.isLoading ? "Recording…" : "Record Payment"}
          </button>
        }
      />

      <form className="grid gap-4 rounded-xl border border-slate-200 bg-white p-4 md:grid-cols-3">
        <div>
          <label className="block text-sm font-medium text-slate-700">Client *</label>
          <select
            className="mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            {...form.register("client", { valueAsNumber: true, required: "Choose a client" })}
          >
            <option value="">Select…</option>
            {clients?.map((client) => (
              <option key={client.id} value={client.id}>
                {client.name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700">Payment Date *</label>
          <input
            type="date"
            className="mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            {...form.register("payment_date", { required: "Payment date is required" })}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700">Amount Received *</label>
          <input
            type="number"
            step="0.01"
            className="mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            {...form.register("amount_received", { valueAsNumber: true, required: "Amount is required" })}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700">Method *</label>
          <select className="mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm" {...form.register("method")}>
            {paymentMethods.map((method) => (
              <option key={method.value} value={method.value}>
                {method.label}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700">Manual Invoice No. *</label>
          <input
            className="mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            placeholder="Manual invoice reference"
            {...form.register("manual_invoice_no", { required: "Manual invoice number is required" })}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700">Reference / OR</label>
          <input
            className="mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            placeholder="Bank txn or OR"
            {...form.register("reference_no")}
          />
        </div>
        <div className="md:col-span-3">
          <label className="block text-sm font-medium text-slate-700">Optional: Allocate now</label>
          <div className="mt-2 grid gap-3 md:grid-cols-2">
            <select
              className="rounded-md border border-slate-300 px-3 py-2 text-sm"
              {...form.register("statement", { valueAsNumber: true })}
            >
              <option value="">Select statement…</option>
              {statements?.map((stmt) => (
                <option key={stmt.id} value={stmt.id}>
                  {stmt.number ?? "Draft"} — {stmt.client_name} (Balance ₱{Number(stmt.balance).toLocaleString()})
                </option>
              ))}
            </select>
            <input
              type="number"
              step="0.01"
              placeholder="Allocation amount"
              className="rounded-md border border-slate-300 px-3 py-2 text-sm"
              {...form.register("allocation_amount", { valueAsNumber: true })}
            />
          </div>
          <p className="mt-1 text-xs text-slate-500">
            You can allocate to multiple statements later via the payment detail screen.
          </p>
        </div>
      </form>

      <section className="rounded-xl border border-slate-200 bg-white">
        <div className="border-b px-4 py-3 text-sm font-semibold text-slate-700">Recent Payments</div>
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-4 py-2">Client</th>
              <th className="px-4 py-2">Date</th>
              <th className="px-4 py-2">Amount</th>
              <th className="px-4 py-2">Method</th>
              <th className="px-4 py-2">Remaining</th>
              <th className="px-4 py-2">Status</th>
              <th className="px-4 py-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            {payments && payments.length > 0 ? (
              payments.map((payment) => (
                <tr key={payment.id} className="hover:bg-slate-50">
                  <td className="px-4 py-2 font-medium">{payment.client_name}</td>
                  <td className="px-4 py-2">{payment.payment_date}</td>
                  <td className="px-4 py-2">₱{Number(payment.amount_received).toLocaleString()}</td>
                  <td className="px-4 py-2 text-xs uppercase">{payment.method}</td>
                  <td className="px-4 py-2">₱{Number(payment.remaining_unallocated).toLocaleString()}</td>
                  <td className="px-4 py-2 text-xs uppercase text-slate-500">{payment.status}</td>
                  <td className="px-4 py-2 text-xs">
                    {payment.status !== "verified" && (
                      <button
                        onClick={() => verifyPayment.mutate(payment.id)}
                        className="rounded-md border border-emerald-600 px-3 py-1 text-emerald-600"
                      >
                        Mark Verified
                      </button>
                    )}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={7} className="px-4 py-4 text-center text-xs text-slate-500">
                  No payments recorded yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </section>
    </div>
  );
};

export default PaymentsPage;
