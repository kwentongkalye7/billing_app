import { useMemo, useState } from "react";
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

  const [selectedStatements, setSelectedStatements] = useState<Set<number>>(new Set());
  const [issuingId, setIssuingId] = useState<number | null>(null);

  const issueStatement = useMutation({
    mutationFn: async (statementId: number) => {
      const today = new Date();
      return axiosClient.post(`/billing-statements/${statementId}/issue/`, {
        issue_date: format(today, "yyyy-MM-dd"),
        due_date: format(addDays(today, 15), "yyyy-MM-dd"),
      });
    },
    onMutate: (statementId: number) => {
      setIssuingId(statementId);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["statements"] }),
    onError: (error: any) => {
      alert(error.response?.data?.detail ?? "Unable to issue statement.");
    },
    onSettled: () => {
      setIssuingId(null);
    },
  });

  const batchIssue = useMutation({
    mutationFn: async (statementIds: number[]) => {
      const today = new Date();
      return axiosClient.post("/billing-statements/batch-issue/", {
        statement_ids: statementIds,
        issue_date: format(today, "yyyy-MM-dd"),
        due_date: format(addDays(today, 15), "yyyy-MM-dd"),
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["statements"] });
      setSelectedStatements(new Set());
    },
    onError: (error: any) => {
      alert(error.response?.data?.detail ?? "Unable to issue selected statements.");
    },
  });

  const runRetainerCycle = useMutation({
    mutationFn: (period: string) => axiosClient.post("/engagements/run-cycle/", { period }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["statements"] }),
    onError: (error: any) => {
      alert(error.response?.data?.detail ?? "Unable to start retainer cycle.");
    },
  });

  const handleRunCycle = async () => {
    const period = prompt("Generate retainer drafts for period (YYYY-MM)?", format(new Date(), "yyyy-MM"));
    if (!period) return;
    await runRetainerCycle.mutateAsync(period);
    alert("Retainer cycle triggered. Drafts will appear once generated.");
  };

  const toggleStatementSelection = (statementId: number, checked: boolean) => {
    setSelectedStatements((prev) => {
      const next = new Set(prev);
      if (checked) {
        next.add(statementId);
      } else {
        next.delete(statementId);
      }
      return next;
    });
  };

  const allSelectableIds = useMemo(
    () =>
      (statements ?? [])
        .filter((stmt) => stmt.status === "draft" || stmt.status === "pending_review")
        .map((stmt) => stmt.id),
    [statements]
  );

  const allSelected = allSelectableIds.length > 0 && allSelectableIds.every((id) => selectedStatements.has(id));

  const toggleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedStatements(new Set(allSelectableIds));
    } else {
      setSelectedStatements(new Set());
    }
  };

  const handleBatchIssue = async () => {
    if (!selectedStatements.size) return;
    await batchIssue.mutateAsync(Array.from(selectedStatements));
  };

  const isMutating = issueStatement.isLoading || batchIssue.isLoading || runRetainerCycle.isLoading;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Statements of Account"
        description="Draft, review, issue, and refresh SOAs."
        actions={
          <div className="flex items-center gap-2">
            <button
              onClick={handleRunCycle}
              className="rounded-md border border-primary px-4 py-2 text-sm font-semibold text-primary"
            >
              Run Retainer Cycle
            </button>
            <button
              onClick={handleBatchIssue}
              disabled={!selectedStatements.size || batchIssue.isLoading}
              className="rounded-md bg-primary px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
            >
              {batchIssue.isLoading ? "Issuing…" : `Issue Selected (${selectedStatements.size})`}
            </button>
          </div>
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
              <th className="px-4 py-2 w-10 text-center">
                <input
                  type="checkbox"
                  checked={allSelected}
                  onChange={(event) => toggleSelectAll(event.target.checked)}
                  disabled={!allSelectableIds.length}
                />
              </th>
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
                <td colSpan={7} className="px-4 py-4 text-center text-xs text-slate-500">
                  Loading statements…
                </td>
              </tr>
            ) : statements && statements.length > 0 ? (
              statements.map((stmt) => {
                const selectable = stmt.status === "draft" || stmt.status === "pending_review";
                const isChecked = selectedStatements.has(stmt.id);
                return (
                  <tr key={stmt.id} className="hover:bg-slate-50">
                    <td className="px-4 py-2 text-center">
                      <input
                        type="checkbox"
                        checked={isChecked}
                        onChange={(event) => toggleStatementSelection(stmt.id, event.target.checked)}
                        disabled={!selectable}
                      />
                    </td>
                    <td className="px-4 py-2 font-medium">{stmt.number ?? "Draft"}</td>
                    <td className="px-4 py-2">{stmt.client_name}</td>
                    <td className="px-4 py-2">{stmt.period}</td>
                    <td className="px-4 py-2 text-xs uppercase text-slate-500">{stmt.status}</td>
                    <td className="px-4 py-2 text-right font-semibold">
                      ₱{Number(stmt.balance).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </td>
                    <td className="px-4 py-2 text-xs">
                      {selectable ? (
                        <button
                          onClick={() => issueStatement.mutate(stmt.id)}
                          className="rounded-md bg-primary px-3 py-1 text-white disabled:cursor-not-allowed disabled:opacity-60"
                          disabled={issuingId === stmt.id}
                        >
                          {issuingId === stmt.id ? "Issuing…" : "Issue & PDF"}
                        </button>
                      ) : stmt.pdf_url ? (
                        <a href={stmt.pdf_url} target="_blank" rel="noreferrer" className="text-primary underline">
                          View PDF
                        </a>
                      ) : (
                        <span className="text-slate-400">No PDF</span>
                      )}
                    </td>
                  </tr>
                );
              })
            ) : (
              <tr>
                <td colSpan={7} className="px-4 py-4 text-center text-xs text-slate-500">
                  No statements yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </section>
      {isMutating && <p className="text-xs text-slate-500">Processing…</p>}
    </div>
  );
};

export default StatementsPage;
