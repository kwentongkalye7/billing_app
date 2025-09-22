import { useQuery } from "@tanstack/react-query";
import { format } from "date-fns";

import { axiosClient } from "../api/client";
import { PageHeader } from "../components/PageHeader";

interface AgingResponse {
  as_of: string;
  buckets: Record<string, number>;
}

interface CollectionsResponse {
  rows: Array<{ payment_date: string; method: string; total_amount: number }>;
}

interface UnappliedResponse {
  rows: Array<{ "client__name": string; total_amount: number }>;
}

const ReportsPage = () => {
  const { data: aging } = useQuery<AgingResponse>({
    queryKey: ["reports", "aging"],
    queryFn: async () => {
      const as_of = format(new Date(), "yyyy-MM-dd");
      const { data } = await axiosClient.get<AgingResponse>(`/reports/aging/?as_of=${as_of}`);
      return data;
    },
  });

  const { data: collections } = useQuery<CollectionsResponse>({
    queryKey: ["reports", "collections"],
    queryFn: async () => {
      const { data } = await axiosClient.get<CollectionsResponse>("/reports/collections/");
      return data;
    },
  });

  const { data: unapplied } = useQuery<UnappliedResponse>({
    queryKey: ["reports", "unapplied"],
    queryFn: async () => {
      const { data } = await axiosClient.get<UnappliedResponse>("/reports/unapplied-credits/");
      return data;
    },
  });

  return (
    <div className="space-y-6">
      <PageHeader title="Reports" description="Key metrics for collectors and reviewers." />

      <section className="rounded-xl border border-slate-200 bg-white p-4">
        <h3 className="text-sm font-semibold text-slate-700">Aging Summary</h3>
        <p className="text-xs text-slate-500">As of {aging?.as_of}</p>
        <div className="mt-3 grid gap-3 md:grid-cols-4">
          {aging &&
            Object.entries(aging.buckets).map(([bucket, amount]) => (
              <div key={bucket} className="rounded-lg bg-slate-50 p-3 text-center">
                <div className="text-xs uppercase text-slate-500">{bucket}</div>
                <div className="text-lg font-semibold">₱{Number(amount).toLocaleString()}</div>
              </div>
            ))}
        </div>
      </section>

      <section className="rounded-xl border border-slate-200 bg-white">
        <div className="border-b px-4 py-3 text-sm font-semibold text-slate-700">Collections Register</div>
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-4 py-2">Date</th>
              <th className="px-4 py-2">Method</th>
              <th className="px-4 py-2">Total</th>
            </tr>
          </thead>
          <tbody>
            {collections?.rows?.length ? (
              collections.rows.map((row, idx) => (
                <tr key={`${row.payment_date}-${idx}`} className="hover:bg-slate-50">
                  <td className="px-4 py-2">{row.payment_date}</td>
                  <td className="px-4 py-2 text-xs uppercase">{row.method}</td>
                  <td className="px-4 py-2">₱{Number(row.total_amount).toLocaleString()}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={3} className="px-4 py-4 text-center text-xs text-slate-500">
                  No payments within the selected window.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </section>

      <section className="rounded-xl border border-slate-200 bg-white">
        <div className="border-b px-4 py-3 text-sm font-semibold text-slate-700">Unapplied Credits</div>
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-4 py-2">Client</th>
              <th className="px-4 py-2">Total Credit</th>
            </tr>
          </thead>
          <tbody>
            {unapplied?.rows?.length ? (
              unapplied.rows.map((row) => (
                <tr key={row["client__name"]} className="hover:bg-slate-50">
                  <td className="px-4 py-2 font-medium">{row["client__name"]}</td>
                  <td className="px-4 py-2">₱{Number(row.total_amount).toLocaleString()}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={2} className="px-4 py-4 text-center text-xs text-slate-500">
                  No open credits. Great job!
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </section>
    </div>
  );
};

export default ReportsPage;
