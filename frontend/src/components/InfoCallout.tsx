interface Props {
  title: string;
  children: React.ReactNode;
}

export const InfoCallout = ({ title, children }: Props) => (
  <div className="rounded-lg border border-blue-200 bg-blue-50 p-4 text-sm text-blue-800">
    <h3 className="mb-1 font-semibold">{title}</h3>
    <div className="space-y-1 text-blue-900">{children}</div>
  </div>
);
