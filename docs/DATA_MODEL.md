# Unified Billing — Data Model

This document summarizes the core entities implemented in the Django backend. For full field definitions, review the corresponding Django models.

## Client & Contacts
- **Client** (`clients.models.Client`)
  - `name`, `normalized_name`, `status`, `billing_address`, `tin`, `tags`, `aliases`, `group`
  - Branding overrides: `branding_logo`, `branding_header_note`
  - Audit fields: `created_at`, `updated_at`, `created_by`, `updated_by`
- **Contact**
  - `client`, `name`, `email`, `phone`, `role`, `is_billing_recipient`

## Engagements
- **Engagement** (`engagements.models.Engagement`)
  - `client`, `type` (`retainer` | `special`)
  - `title`, `summary`, `status`, `start_date`, `end_date`
  - Retainer metadata: `base_fee`, `recurrence`, `billing_day`, `default_description`, `last_generated_period`

## Statements
- **BillingStatement** (`statements.models.BillingStatement`)
  - `number`, `client`, `engagement`, `period`
  - `issue_date`, `due_date`, `currency`, `notes`, `status`
  - Financials: `sub_total`, `paid_to_date`, `balance`
  - PDF metadata: `pdf_path`
  - `idempotency_hash` prevents duplicate retainer drafts per period
- **BillingItem**
  - `billing_statement`, `description`, `qty`, `unit`, `unit_price`, `line_total`

## Payments
- **Payment** (`payments.models.Payment`)
  - `client`, `payment_date`, `amount_received`, `currency`
  - `method` (cash, check, BPI transfer, BDO transfer, LBP transfer, GCash)
  - `manual_invoice_no`, `reference_no`, `notes`
  - Status workflow: `draft → posted → verified` (or `void`)
  - Audit: `recorded_by`, `verified_by`, `verified_at`
- **PaymentAllocation**
  - `payment`, `billing_statement`, `amount_applied`
  - Saves recompute statement balances and settlement status
- **UnappliedCredit**
  - `client`, `source_payment`, `amount`, `reason`, `status` (`open` | `applied` | `refunded`)

## Sequences
- **Sequence** (`sequences.models.Sequence`)
  - `code`, `name`, `prefix`, `padding`, `current_value`, `reset_rule`, `last_reset_at`
  - `assign_next` handles atomic numbering, default `SOA-YYYY-####`

## Audit
- **AuditLog** (`audit.models.AuditLog`)
  - `actor`, `action`, `entity_type`, `entity_id`
  - `before`, `after`, optional `metadata`
  - Populated via `audit.utils.log_action`

## Reports (Read Models)
- Aging buckets computed from `BillingStatement.balance` and `due_date`
- Collections register aggregates `Payment.amount_received` by date & method
- Unapplied credit report surfaces open `UnappliedCredit` per client

## Status & Business Rules Recap
- Statements: `draft → pending_review → issued → settled` (void retains number)
- Payments: manual allocation only; any remainder becomes `UnappliedCredit`
- Retainer cycle runner is idempotent per `client + engagement + period`
- Monetary values stored as `Decimal(12,2)`; all totals exclude tax/withholding
