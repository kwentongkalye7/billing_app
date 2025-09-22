import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";

import { axiosClient } from "../api/client";
import { InfoCallout } from "../components/InfoCallout";
import { PageHeader } from "../components/PageHeader";
import type { Client } from "../types/api";

interface ClientFormValues {
  name: string;
  billing_address: string;
  tin: string;
  status: "active" | "inactive";
}

const defaultValues: ClientFormValues = {
  name: "",
  billing_address: "",
  tin: "",
  status: "active",
};

const ClientsPage = () => {
  const queryClient = useQueryClient();
  const { data: clients, isLoading } = useQuery<Client[]>({
    queryKey: ["clients"],
    queryFn: async () => {
      const { data } = await axiosClient.get<Client[]>("/clients/?ordering=name");
      return data;
    },
  });

  const [selectedClient, setSelectedClient] = useState<Client | null>(null);
  const form = useForm<ClientFormValues>({ defaultValues });

  const resetForm = () => {
    setSelectedClient(null);
    form.reset(defaultValues);
  };

  const createClient = useMutation({
    mutationFn: (values: ClientFormValues) => axiosClient.post("/clients/", values),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["clients"] });
      resetForm();
    },
    onError: (error: any) => {
      alert(error.response?.data?.detail ?? "Unable to create client.");
    },
  });

  const updateClient = useMutation({
    mutationFn: ({ id, values }: { id: number; values: Partial<ClientFormValues> }) =>
      axiosClient.patch(`/clients/${id}/`, values),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["clients"] });
      resetForm();
    },
    onError: (error: any) => {
      alert(error.response?.data?.detail ?? "Unable to update client.");
    },
  });

  const deleteClient = useMutation({
    mutationFn: (clientId: number) => axiosClient.delete(`/clients/${clientId}/`),
    onSuccess: (_, clientId) => {
      queryClient.invalidateQueries({ queryKey: ["clients"] });
      if (selectedClient?.id === clientId) {
        resetForm();
      }
    },
    onError: (error: any) => {
      alert(error.response?.data?.detail ?? "Unable to delete client.");
    },
  });

  const onSubmit = form.handleSubmit(async (values) => {
    if (selectedClient) {
      await updateClient.mutateAsync({ id: selectedClient.id, values });
    } else {
      await createClient.mutateAsync(values);
    }
  });

  const handleEdit = (client: Client) => {
    setSelectedClient(client);
    form.reset({
      name: client.name,
      billing_address: client.billing_address ?? "",
      tin: client.tin ?? "",
      status: client.status,
    });
  };

  const handleDelete = (client: Client) => {
    if (confirm(`Delete client "${client.name}"? This cannot be undone.`)) {
      deleteClient.mutate(client.id);
    }
  };

  const toggleStatus = (client: Client) => {
    const nextStatus = client.status === "active" ? "inactive" : "active";
    updateClient.mutate({ id: client.id, values: { status: nextStatus } });
  };

  const actionLabel = useMemo(() => (selectedClient ? "Update Client" : "Save Client"), [selectedClient]);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Clients"
        description="Unified master list across retainers and special engagements."
        actions={
          <div className="flex items-center gap-2">
            <button
              onClick={onSubmit}
              disabled={createClient.isLoading || updateClient.isLoading}
              className="rounded-md bg-primary px-4 py-2 text-sm font-semibold text-white"
            >
              {createClient.isLoading || updateClient.isLoading ? "Saving…" : actionLabel}
            </button>
            {selectedClient && (
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
      <InfoCallout title="Tips for clean imports">
        <p>- Normalize client names (e.g., remove commas) to keep dedupe deterministic.</p>
        <p>- Capture billing TIN for reporting. Leave blank if unavailable.</p>
      </InfoCallout>

      <form onSubmit={onSubmit} className="grid gap-4 rounded-xl border border-slate-200 bg-white p-4 md:grid-cols-4">
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
        <div className="md:col-span-1">
          <label className="block text-sm font-medium text-slate-700">Status</label>
          <select
            className="mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            {...form.register("status")}
          >
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
        </div>
      </form>

      <section className="rounded-xl border border-slate-200 bg-white">
        <div className="border-b px-4 py-3 text-sm font-semibold text-slate-700">Clients</div>
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-4 py-2">Name</th>
              <th className="px-4 py-2">Status</th>
              <th className="px-4 py-2">TIN</th>
              <th className="px-4 py-2">Tags</th>
              <th className="px-4 py-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr>
                <td colSpan={5} className="px-4 py-4 text-center text-xs text-slate-500">
                  Loading clients…
                </td>
              </tr>
            ) : clients && clients.length > 0 ? (
              clients.map((client) => (
                <tr key={client.id} className="hover:bg-slate-50">
                  <td className="px-4 py-2 font-medium">{client.name}</td>
                  <td className="px-4 py-2">
                    <span
                      className={`rounded-full px-2 py-0.5 text-xs ${
                        client.status === "active"
                          ? "bg-emerald-100 text-emerald-700"
                          : "bg-slate-200 text-slate-600"
                      }`}
                    >
                      {client.status}
                    </span>
                  </td>
                  <td className="px-4 py-2">{client.tin ?? "—"}</td>
                  <td className="px-4 py-2 text-xs text-slate-500">{client.tags?.join(", ")}</td>
                  <td className="px-4 py-2">
                    <div className="flex flex-wrap items-center gap-2">
                      <button
                        onClick={() => handleEdit(client)}
                        className="rounded-md border border-slate-300 px-2 py-1 text-xs text-slate-600"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => toggleStatus(client)}
                        className="rounded-md border border-slate-300 px-2 py-1 text-xs text-slate-600"
                      >
                        {client.status === "active" ? "Mark Inactive" : "Re-activate"}
                      </button>
                      <button
                        onClick={() => handleDelete(client)}
                        className="rounded-md border border-red-300 px-2 py-1 text-xs text-red-600"
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={5} className="px-4 py-4 text-center text-xs text-slate-500">
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
