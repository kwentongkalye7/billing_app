interface Props {
  title: string;
  description?: string;
  actions?: React.ReactNode;
}

export const PageHeader = ({ title, description, actions }: Props) => (
  <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
    <div>
      <h2 className="text-2xl font-semibold text-slate-900">{title}</h2>
      {description && <p className="text-sm text-slate-500">{description}</p>}
    </div>
    {actions && <div className="flex items-center gap-2">{actions}</div>}
  </div>
);
