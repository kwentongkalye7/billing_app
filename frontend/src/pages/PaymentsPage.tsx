import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";

import { axiosClient } from "../api/client";
import { PageHeader } from "../components/PageHeader";
import type { BillingStatement, Client, Payment } from "../types/api";

interface PaymentForm {
  client: number | "";
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

const defaultValues = (): PaymentForm => ({
  client: "",
  payment_date: new Date().toISOString().slice(0, 10),
  amount_received: 0,
  method: "cash",
  manual_invoice_no: "",
  reference_no: "",
  note: "",
  statement: undefined,
  allocation_amount: undefined,
});

const PaymentsPage = () => {
  const queryClient = useQueryClient();
  const { data: clients } = useQuery<Client[]>({
    queryKey: ["clients", "all"],
    queryFn: async () => {
      const { data } = await axiosClient.get<Client[]>("/clients/?ordering=name");
      return data;
    },
  });

  const { data: statements } = useQuery<BillingStatement[]>({
    queryKey: ["statements", { status: "open" }],
    queryFn: async () => {
      const { data } = await axiosClient.get<BillingStatement[]>("/billing-statements/?status=issued");
      return data;
    },
  });

  const { data: payments, isLoading: paymentsLoading } = useQuery<Payment[]>({
    queryKey: ["payments"],
    queryFn: async () => {
      const { data } = await axiosClient.get<Payment[]>("/payments/?ordering=-payment_date,-created_at");
      return data;
    },
  });

  const [selectedPayment, setSelectedPayment] = useState<Payment | null>(null);
  const form = useForm<PaymentForm>({ defaultValues: defaultValues() });

  const resetForm = () => {
    setSelectedPayment(null);
    form.reset(defaultValues());
  };

  const invalidatePaymentQueries = () => {
    const isPayments = ({ queryKey }: { queryKey: unknown }) => Array.isArray(queryKey) && queryKey[0] === "payments";
    const isStatements = ({ queryKey }: { queryKey: unknown }) => Array.isArray(queryKey) && queryKey[0] === "statements";

    queryClient.invalidateQueries({ predicate: isPayments });
    queryClient.removeQueries({ predicate: isStatements });
  };

  const createPayment = useMutation({
    mutationFn: (payload: any) => axiosClient.post("/payments/", payload),
    onSuccess: () => {
      invalidatePaymentQueries();
      resetForm();
    },
    onError: (error: any) => {
      alert(error.response?.data?.manual_invoice_no ?? error.response?.data?.detail ?? "Unable to record payment.");
    },
  });

  const updatePayment = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: any }) => axiosClient.patch(`/payments/${id}/`, payload),
    onSuccess: () => {
      invalidatePaymentQueries();
      resetForm();
    },
    onError: (error: any) => {
      alert(error.response?.data?.manual_invoice_no ?? error.response?.data?.detail ?? "Unable to update payment.");
    },
  });

  const deletePayment = useMutation({
    mutationFn: (id: number) => axiosClient.delete(`/payments/${id}/`),
    onSuccess: () => {
      invalidatePaymentQueries();
      resetForm();
    },
    onError: (error: any) => {
      alert(error.response?.data?.detail ?? "Unable to delete payment.");
    },
  });

  const verifyPayment = useMutation({
    mutationFn: (paymentId: number) => axiosClient.post(`/payments/${paymentId}/verify/`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["payments"] }),
    onError: (error: any) => {
      alert(error.response?.data?.detail ?? "Unable to verify payment.");
    },
  });

  const onSubmit = form.handleSubmit(async (values) => {
    if (createPayment.isLoading || updatePayment.isLoading) return;

    const clientId = Number(values.client);
    if (!clientId) {
      form.setError("client", { type: "manual", message: "Client is required" });
      return;
    }
    if (!values.manual_invoice_no) {
      form.setError("manual_invoice_no", { type: "manual", message: "Manual invoice number is required" });
      return;
    }
    if (!values.amount_received || values.amount_received <= 0) {
      form.setError("amount_received", { type: "manual", message: "Amount must be greater than zero" });
      return;
    }

    const payload: any = {
      client: clientId,
      payment_date: values.payment_date,
      amount_received: values.amount_received,
      method: values.method,
      manual_invoice_no: values.manual_invoice_no,
      reference_no: values.reference_no ?? "",
      notes: values.note ?? "",
      allocations: [],
    };

    const hasAllocation =
      values.statement &&
      values.allocation_amount !== undefined &&
      !Number.isNaN(values.allocation_amount) &&
      values.allocation_amount > 0;

    if (hasAllocation) {
      payload.allocations.push({
        billing_statement: values.statement,
        amount_applied: values.allocation_amount,
      });
    }

    try {
      if (selectedPayment) {
        await updatePayment.mutateAsync({ id: selectedPayment.id, payload });
      } else {
        await createPayment.mutateAsync(payload);
      }
    } catch (error: any) {
      const manualInvoiceErr = error.response?.data?.manual_invoice_no;
      if (manualInvoiceErr) {
        form.setError("manual_invoice_no", { type: "manual", message: manualInvoiceErr });
      }
    }
  });

  const handleEdit = (payment: Payment) => {
    setSelectedPayment(payment);
    form.reset({
      client: payment.client,
      payment_date: payment.payment_date,
      amount_received: Number(payment.amount_received),
      method: payment.method,
      manual_invoice_no: payment.manual_invoice_no,
      reference_no: payment.reference_no ?? "",
      note: payment.notes ?? "",
      statement: undefined,
      allocation_amount: undefined,
    });
  };

  const handleDelete = (payment: Payment) => {
    if (confirm(`Delete payment dated ${payment.payment_date} for ${payment.client_name}?`)) {
      deletePayment.mutate(payment.id);
    }
  };

  const actionLabel = useMemo(() => (selectedPayment ? "Update Payment" : "Record Payment"), [selectedPayment]);
  const isSubmitting = createPayment.isLoading || updatePayment.isLoading;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Payments"
        description="Record settlements, enforce manual allocation, and track unapplied credits."
        actions={
          <div className="flex items-center gap-2">
            <button
              onClick={onSubmit}
              disabled={isSubmitting}
              className="rounded-md bg-primary px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
            >
              {isSubmitting ? "Saving…" : actionLabel}
            </button>
            {selectedPayment && (
              <button
                onClick={resetForm}
                className="rounded-md border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-600"
              >
                Cancel
              </button>
            )}
          </div>
        }
      />

      <form className="grid gap-4 rounded-xl border border-slate-200 bg-white p-4 md:grid-cols-3" onSubmit={onSubmit}>
        <div>
          <label className="block text-sm font-medium text-slate-700">Client *</label>
          <select
            className="mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            {...form.register("client")}
          >
            <option value="">Select…</option>
            {clients?.map((client) => (
              <option key={client.id} value={client.id}>
                {client.name}
              </option>
            ))}
          </select>
          {form.formState.errors.client && (
            <p className="mt-1 text-xs text-red-600">{form.formState.errors.client.message}</p>
          )}
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700">Payment Date *</label>
          <input
            type="date"
            className="mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            {...form.register("payment_date")}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700">Amount Received *</label>
          <input
            type="number"
            step="0.01"
            className="mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            {...form.register("amount_received", { valueAsNumber: true })}
          />
          {form.formState.errors.amount_received && (
            <p className="mt-1 text-xs text-red-600">{form.formState.errors.amount_received.message}</p>
          )}
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
            {...form.register("manual_invoice_no")}
          />
          {form.formState.errors.manual_invoice_no && (
            <p className="mt-1 text-xs text-red-600">{form.formState.errors.manual_invoice_no.message}</p>
          )}
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
            {paymentsLoading ? (
              <tr>
                <td colSpan={7} className="px-4 py-4 text-center text-xs text-slate-500">
                  Loading payments…
                </td>
              </tr>
            ) : payments && payments.length > 0 ? (
              payments.map((payment) => (
                <tr key={payment.id} className="hover:bg-slate-50">
                  <td className="px-4 py-2 font-medium">{payment.client_name}</td>
                  <td className="px-4 py-2">{payment.payment_date}</td>
                  <td className="px-4 py-2">₱{Number(payment.amount_received).toLocaleString()}</td>
                  <td className="px-4 py-2 text-xs uppercase">{payment.method}</td>
                  <td className="px-4 py-2">₱{Number(payment.remaining_unallocated).toLocaleString()}</td>
                  <td className="px-4 py-2 text-xs uppercase text-slate-500">{payment.status}</td>
                  <td className="px-4 py-2 text-xs">
                    <div className="flex flex-wrap items-center gap-2">
                      <button
                        onClick={() => handleEdit(payment)}
                        className="rounded-md border border-slate-300 px-2 py-1 text-slate-600"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(payment)}
                        className="rounded-md border border-red-300 px-2 py-1 text-red-600"
                      >
                        Delete
                      </button>
                      {payment.status !== "verified" && (
                        <button
                          onClick={() => verifyPayment.mutate(payment.id)}
                          className="rounded-md border border-emerald-300 px-2 py-1 text-emerald-600 disabled:opacity-50"
                          disabled={verifyPayment.isLoading && verifyPayment.variables === payment.id}
                        >
                          {verifyPayment.isLoading && verifyPayment.variables === payment.id ? "Verifying…" : "Mark Verified"}
                        </button>
                      )}
                    </div>
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
