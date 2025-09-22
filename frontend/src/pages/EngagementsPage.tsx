import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";

import { axiosClient } from "../api/client";
import { PageHeader } from "../components/PageHeader";
import type { Client, Engagement } from "../types/api";

interface FormValues {
  client: number;
  type: "retainer" | "special";
  title: string;
  base_fee?: number;
  start_date: string;
}

const EngagementsPage = () => {
  const queryClient = useQueryClient();
  const { data: clients } = useQuery<Client[]>({
    queryKey: ["clients"],
    queryFn: async () => {
      const { data } = await axiosClient.get<Client[]>("/clients/?status=active");
      return data;
    },
  });

  const { data: engagements } = useQuery<Engagement[]>({
    queryKey: ["engagements"],
    queryFn: async () => {
      const { data } = await axiosClient.get<Engagement[]>("/engagements/?ordering=client");
      return data;
    },
  });

  const form = useForm<FormValues>({
    defaultValues: {
      client: undefined,
      type: "retainer",
      title: "",
      base_fee: 0,
      start_date: new Date().toISOString().slice(0, 10),
    },
  });

  const createEngagement = useMutation({
    mutationFn: (values: FormValues) => axiosClient.post("/engagements/", values),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["engagements"] });
      form.reset();
    },
  });

  const onSubmit = form.handleSubmit(async (values) => {
    await createEngagement.mutateAsync(values);
  });

  return (
    <div className="space-y-6">
      <PageHeader
        title="Engagements"
        description="Create retainers or special engagements to generate statements."
        actions={
          <button
            onClick={onSubmit}
            disabled={createEngagement.isLoading}
            className="rounded-md bg-primary px-4 py-2 text-sm font-semibold text-white"
          >
            {createEngagement.isLoading ? "Saving…" : "Save Engagement"}
          </button>
        }
      />

      <form className="grid gap-4 rounded-xl border border-slate-200 bg-white p-4 md:grid-cols-5" onSubmit={onSubmit}>
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-slate-700">Client *</label>
          <select
            className="mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            {...form.register("client", { valueAsNumber: true, required: "Select a client" })}
          >
            <option value="">Select…</option>
            {clients?.map((client) => (
              <option value={client.id} key={client.id}>
                {client.name}
              </option>
            ))}
          </select>
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
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700">Base Fee (for retainers)</label>
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
            </tr>
          </thead>
          <tbody>
            {engagements && engagements.length > 0 ? (
              engagements.map((eng) => (
                <tr key={eng.id} className="hover:bg-slate-50">
                  <td className="px-4 py-2 font-medium">{eng.client_name}</td>
                  <td className="px-4 py-2">{eng.title}</td>
                  <td className="px-4 py-2 uppercase text-xs">{eng.type}</td>
                  <td className="px-4 py-2 text-xs text-slate-500">{eng.status}</td>
                  <td className="px-4 py-2">{eng.last_generated_period ?? "—"}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={5} className="px-4 py-4 text-center text-xs text-slate-500">
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
