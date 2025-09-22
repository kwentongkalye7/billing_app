import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";

import { axiosClient } from "../api/client";
import { PageHeader } from "../components/PageHeader";
import { InfoCallout } from "../components/InfoCallout";
import type { Client } from "../types/api";

interface CreateClientForm {
  name: string;
  billing_address?: string;
  tin?: string;
}

const ClientsPage = () => {
  const queryClient = useQueryClient();
  const { data: clients } = useQuery<Client[]>({
    queryKey: ["clients"],
    queryFn: async () => {
      const { data } = await axiosClient.get<Client[]>("/clients/?ordering=name");
      return data;
    },
  });

  const form = useForm<CreateClientForm>({
    defaultValues: { name: "", billing_address: "", tin: "" },
  });

  const createClient = useMutation({
    mutationFn: (values: CreateClientForm) => axiosClient.post("/clients/", values),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["clients"] });
      form.reset();
    },
  });

  const onSubmit = form.handleSubmit(async (values) => {
    await createClient.mutateAsync(values);
  });

  return (
    <div className="space-y-6">
      <PageHeader
        title="Clients"
        description="Unified master list across retainers and special engagements."
        actions={
          <button
            onClick={onSubmit}
            disabled={createClient.isLoading}
            className="rounded-md bg-primary px-4 py-2 text-sm font-semibold text-white"
          >
            {createClient.isLoading ? "Saving…" : "Save Client"}
          </button>
        }
      />
      <InfoCallout title="Tips for clean imports">
        <p>
          - Normalize client names (e.g., remove commas) to keep dedupe deterministic.
        </p>
        <p>- Capture billing TIN for reporting. Leave blank if unavailable.</p>
      </InfoCallout>

      <form onSubmit={onSubmit} className="grid gap-4 rounded-xl border border-slate-200 bg-white p-4 md:grid-cols-3">
        <div className="md:col-span-1">
          <label className="block text-sm font-medium text-slate-700">Client Name *</label>
          <input
            className="mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-primary focus:ring-primary"
            placeholder="Acme Corporation"
            {...form.register("name", { required: "Client name is required" })}
          />
          {form.formState.errors.name && (
            <p className="mt-1 text-xs text-red-600">{form.formState.errors.name.message}</p>
          )}
        </div>
        <div className="md:col-span-1">
          <label className="block text-sm font-medium text-slate-700">Billing Address</label>
          <textarea
            rows={3}
            className="mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-primary focus:ring-primary"
            placeholder="123 Finance St., Makati City"
            {...form.register("billing_address")}
          />
        </div>
        <div className="md:col-span-1">
          <label className="block text-sm font-medium text-slate-700">TIN</label>
          <input
            className="mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-primary focus:ring-primary"
            placeholder="123-456-789"
            {...form.register("tin")}
          />
          <p className="mt-1 text-xs text-slate-500">Optional, but helpful for manual invoices.</p>
        </div>
      </form>

      <section className="rounded-xl border border-slate-200 bg-white">
        <div className="border-b px-4 py-3 text-sm font-semibold text-slate-700">Active Clients</div>
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-4 py-2">Name</th>
              <th className="px-4 py-2">Status</th>
              <th className="px-4 py-2">TIN</th>
              <th className="px-4 py-2">Tags</th>
            </tr>
          </thead>
          <tbody>
            {clients?.map((client) => (
              <tr key={client.id} className="hover:bg-slate-50">
                <td className="px-4 py-2 font-medium">{client.name}</td>
                <td className="px-4 py-2">
                  <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-xs text-emerald-700">
                    {client.status}
                  </span>
                </td>
                <td className="px-4 py-2">{client.tin ?? "—"}</td>
                <td className="px-4 py-2 text-xs text-slate-500">{client.tags?.join(", ")}</td>
              </tr>
            )) ?? (
              <tr>
                <td colSpan={4} className="px-4 py-4 text-center text-xs text-slate-500">
                  No clients yet. Use the form above or import via CSV from the admin.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </section>
    </div>
  );
};

export default ClientsPage;
