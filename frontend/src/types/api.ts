export type Role = "admin" | "biller" | "reviewer" | "viewer";

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  display_name: string;
  role: Role;
  permissions: Record<string, boolean>;
}

export interface Client {
  id: number;
  name: string;
  status: "active" | "inactive";
  billing_address?: string;
  tin?: string;
  tags: string[];
  aliases: string[];
  group?: string;
  branding_logo?: string;
  branding_header_note?: string;
}

export interface Engagement {
  id: number;
  client: number;
  client_name: string;
  type: "retainer" | "special";
  title: string;
  status: "active" | "suspended" | "ended";
  start_date: string;
  end_date?: string | null;
  base_fee: string;
  last_generated_period?: string;
}

export interface BillingItem {
  id: number;
  description: string;
  qty: string;
  unit: string;
  unit_price: string;
  line_total: string;
}

export interface BillingStatement {
  id: number;
  number?: string;
  client: number;
  client_name: string;
  engagement: number;
  engagement_title: string;
  period: string;
  issue_date?: string | null;
  due_date?: string | null;
  status: string;
  status_display: string;
  sub_total: string;
  paid_to_date: string;
  balance: string;
  pdf_url?: string | null;
  items: BillingItem[];
}

export interface PaymentAllocation {
  id: number;
  billing_statement: number;
  amount_applied: string;
}

export interface Payment {
  id: number;
  client: number;
  client_name: string;
  payment_date: string;
  amount_received: string;
  method: string;
  manual_invoice_no: string;
  reference_no?: string;
  notes?: string;
  status: string;
  remaining_unallocated: string;
  allocations?: PaymentAllocation[];
}

export interface AgingBucketRow {
  bucket: string;
  total_balance: string;
}
