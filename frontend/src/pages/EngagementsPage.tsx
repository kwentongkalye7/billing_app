import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";

import { axiosClient } from "../api/client";
import { PageHeader } from "../components/PageHeader";
import type { Client, Engagement } from "../types/api";

interface EngagementFormValues {
  client: number | "";
  type: "retainer" | "special";
  title: string;
  base_fee: number;
  start_date: string;
  status: "active" | "suspended" | "ended";
  end_date?: string;
}

const defaultValues = (): EngagementFormValues => ({
  client: "",
  type: "retainer",
  title: "",
  base_fee: 0,
  start_date: new Date().toISOString().slice(0, 10),
  status: "active",
  end_date: "",
});

const EngagementsPage = () => {
  const queryClient = useQueryClient();
  const { data: clients } = useQuery<Client[]>({
    queryKey: ["clients", "all"],
    queryFn: async () => {
      const { data } = await axiosClient.get<Client[]>("/clients/?ordering=name");
      return data;
    },
  });

  const { data: engagements, isLoading } = useQuery<Engagement[]>({
    queryKey: ["engagements"],
    queryFn: async () => {
      const { data } = await axiosClient.get<Engagement[]>("/engagements/?ordering=client");
      return data;
    },
  });

  const [selectedEngagement, setSelectedEngagement] = useState<Engagement | null>(null);
  const form = useForm<EngagementFormValues>({ defaultValues: defaultValues() });

  const resetForm = () => {
    setSelectedEngagement(null);
    form.reset(defaultValues());
  };

  const createEngagement = useMutation({
    mutationFn: (payload: { client: number; type: "retainer" | "special"; title: string; base_fee: number; start_date: string; status: "active" | "suspended" | "ended"; end_date: string | null }) =>
      axiosClient.post("/engagements/", payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["engagements"] });
      resetForm();
    },
    onError: (error: any) => {
      alert(error.response?.data?.detail ?? "Unable to create engagement.");
    },
  });

  const updateEngagement = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: Partial<EngagementFormValues> & { end_date?: string | null } }) =>
      axiosClient.patch(`/engagements/${id}/`, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["engagements"] });
      resetForm();
    },
    onError: (error: any) => {
      alert(error.response?.data?.detail ?? "Unable to update engagement.");
    },
  });

  const deleteEngagement = useMutation({
    mutationFn: (id: number) => axiosClient.delete(`/engagements/${id}/`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["engagements"] });
      resetForm();
    },
    onError: (error: any) => {
      alert(error.response?.data?.detail ?? "Unable to delete engagement.");
    },
  });

  const onSubmit = form.handleSubmit(async (values) => {
    const clientId = Number(values.client);
    if (!clientId) {
      form.setError("client", { type: "manual", message: "Client is required" });
      return;
    }
    const payload = {
      client: clientId,
      type: values.type,
      title: values.title,
      base_fee: Number.isFinite(values.base_fee) ? values.base_fee : 0,
      start_date: values.start_date,
      status: values.status,
      end_date: values.end_date ? values.end_date : null,
    };
    if (selectedEngagement) {
      await updateEngagement.mutateAsync({ id: selectedEngagement.id, payload });
    } else {
      await createEngagement.mutateAsync(payload);
    }
  });

  const handleEdit = (engagement: Engagement) => {
    setSelectedEngagement(engagement);
    form.reset({
      client: engagement.client,
      type: engagement.type,
      title: engagement.title,
      base_fee: Number(engagement.base_fee),
      start_date: engagement.start_date,
      status: engagement.status,
      end_date: engagement.end_date ?? "",
    });
  };

  const handleDelete = (engagement: Engagement) => {
    if (confirm(`Delete engagement "${engagement.title}"? This cannot be undone.`)) {
      deleteEngagement.mutate(engagement.id);
    }
  };

  const actionLabel = useMemo(() => (selectedEngagement ? "Update Engagement" : "Save Engagement"), [selectedEngagement]);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Engagements"
        description="Create retainers or special engagements to generate statements."
        actions={
          <div className="flex items-center gap-2">
            <button
              onClick={onSubmit}
              disabled={createEngagement.isLoading || updateEngagement.isLoading}
              className="rounded-md bg-primary px-4 py-2 text-sm font-semibold text-white"
            >
              {createEngagement.isLoading || updateEngagement.isLoading ? "Saving…" : actionLabel}
            </button>
            {selectedEngagement && (
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

      <form className="grid gap-4 rounded-xl border border-slate-200 bg-white p-4 md:grid-cols-6" onSubmit={onSubmit}>
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-slate-700">Client *</label>
          <select
            className="mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            {...form.register("client")}
          >
            <option value="">Select…</option>
            {clients?.map((client) => (
              <option value={client.id} key={client.id}>
                {client.name}
              </option>
            ))}
          </select>
          {form.formState.errors.client && (
            <p className="mt-1 text-xs text-red-600">{form.formState.errors.client.message}</p>
          )}
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700">Type</label>
          <select className="mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm" {...form.register("type")}>
            <option value="retainer">Retainer</option>
            <option value="special">Special</option>
          </select>
        </div>
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-slate-700">Title *</label>
          <input
            className="mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            placeholder="Monthly Compliance"
            {...form.register("title", { required: "Title is required" })}
          />
          {form.formState.errors.title && (
            <p className="mt-1 text-xs text-red-600">{form.formState.errors.title.message}</p>
          )}
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700">Base Fee</label>
          <input
            type="number"
            step="0.01"
            className="mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            {...form.register("base_fee", { valueAsNumber: true })}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700">Start Date</label>
          <input
            type="date"
            className="mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            {...form.register("start_date", { required: "Start date is required" })}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700">Status</label>
          <select className="mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm" {...form.register("status")}>
            <option value="active">Active</option>
            <option value="suspended">Suspended</option>
            <option value="ended">Ended</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700">End Date</label>
          <input
            type="date"
            className="mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            {...form.register("end_date")}
          />
        </div>
      </form>

      <section className="rounded-xl border border-slate-200 bg-white">
        <div className="border-b px-4 py-3 text-sm font-semibold text-slate-700">Engagements</div>
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-4 py-2">Client</th>
              <th className="px-4 py-2">Title</th>
              <th className="px-4 py-2">Type</th>
              <th className="px-4 py-2">Status</th>
              <th className="px-4 py-2">Last Period</th>
              <th className="px-4 py-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr>
                <td colSpan={6} className="px-4 py-4 text-center text-xs text-slate-500">
                  Loading engagements…
                </td>
              </tr>
            ) : engagements && engagements.length > 0 ? (
              engagements.map((eng) => (
                <tr key={eng.id} className="hover:bg-slate-50">
                  <td className="px-4 py-2 font-medium">{eng.client_name}</td>
                  <td className="px-4 py-2">{eng.title}</td>
                  <td className="px-4 py-2 uppercase text-xs">{eng.type}</td>
                  <td className="px-4 py-2 text-xs text-slate-500">{eng.status}</td>
                  <td className="px-4 py-2">{eng.last_generated_period ?? "—"}</td>
                  <td className="px-4 py-2">
                    <div className="flex flex-wrap items-center gap-2">
                      <button
                        onClick={() => handleEdit(eng)}
                        className="rounded-md border border-slate-300 px-2 py-1 text-xs text-slate-600"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(eng)}
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
                <td colSpan={6} className="px-4 py-4 text-center text-xs text-slate-500">
                  No engagements yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </section>
    </div>
  );
};

export default EngagementsPage;
