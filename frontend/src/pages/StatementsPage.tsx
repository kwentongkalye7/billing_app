import { addDays, format } from "date-fns";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { axiosClient } from "../api/client";
import { InfoCallout } from "../components/InfoCallout";
import { PageHeader } from "../components/PageHeader";
import type { BillingStatement } from "../types/api";

const StatementsPage = () => {
  const queryClient = useQueryClient();
  const { data: statements, isLoading } = useQuery<BillingStatement[]>({
    queryKey: ["statements"],
    queryFn: async () => {
      const { data } = await axiosClient.get<BillingStatement[]>("/billing-statements/?ordering=-created_at");
      return data;
    },
  });

  const issueStatement = useMutation({
    mutationFn: (statementId: number) => {
      const today = new Date();
      return axiosClient.post(`/billing-statements/${statementId}/issue/`, {
        issue_date: format(today, "yyyy-MM-dd"),
        due_date: format(addDays(today, 15), "yyyy-MM-dd"),
      });
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["statements"] }),
  });

  const runRetainerCycle = useMutation({
    mutationFn: (period: string) => axiosClient.post("/engagements/run-cycle/", { period }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["statements"] }),
  });

  const handleRunCycle = async () => {
    const period = prompt("Generate retainer drafts for period (YYYY-MM)?", format(new Date(), "yyyy-MM"));
    if (!period) return;
    await runRetainerCycle.mutateAsync(period);
    alert("Retainer cycle triggered. Drafts will appear once generated.");
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Statements of Account"
        description="Draft, review, issue, and refresh SOAs."
        actions={
          <button
            onClick={handleRunCycle}
            className="rounded-md border border-primary px-4 py-2 text-sm font-semibold text-primary"
          >
            Run Retainer Cycle
          </button>
        }
      />
      <InfoCallout title="Issuance workflow">
        <p>Draft → Pending Review (optional) → Issue (assign number & generate PDF) → Payments settle balances.</p>
        <p>Manual invoice numbers are captured only during payment recording per BIR rules.</p>
      </InfoCallout>

      <section className="rounded-xl border border-slate-200 bg-white">
        <div className="border-b px-4 py-3 text-sm font-semibold text-slate-700">Statements</div>
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-4 py-2">Number</th>
              <th className="px-4 py-2">Client</th>
              <th className="px-4 py-2">Period</th>
              <th className="px-4 py-2">Status</th>
              <th className="px-4 py-2 text-right">Balance</th>
              <th className="px-4 py-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr>
                <td colSpan={6} className="px-4 py-4 text-center text-xs text-slate-500">
                  Loading statements…
                </td>
              </tr>
            ) : statements && statements.length > 0 ? (
              statements.map((stmt) => (
                <tr key={stmt.id} className="hover:bg-slate-50">
                  <td className="px-4 py-2 font-medium">{stmt.number ?? "Draft"}</td>
                  <td className="px-4 py-2">{stmt.client_name}</td>
                  <td className="px-4 py-2">{stmt.period}</td>
                  <td className="px-4 py-2 text-xs uppercase text-slate-500">{stmt.status}</td>
                  <td className="px-4 py-2 text-right font-semibold">
                    ₱{Number(stmt.balance).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                  </td>
                  <td className="px-4 py-2 text-xs">
                    {stmt.status === "draft" || stmt.status === "pending_review" ? (
                      <button
                        onClick={() => issueStatement.mutate(stmt.id)}
                        className="rounded-md bg-primary px-3 py-1 text-white"
                      >
                        Issue & PDF
                      </button>
                    ) : stmt.pdf_url ? (
                      <a
                        href={stmt.pdf_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-primary underline"
                      >
                        View PDF
                      </a>
                    ) : (
                      <span className="text-slate-400">No PDF</span>
                    )}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={6} className="px-4 py-4 text-center text-xs text-slate-500">
                  No statements yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </section>
    </div>
  );
};

export default StatementsPage;
