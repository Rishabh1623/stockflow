import { useAlerts } from "../lib/queries";

interface Props {
  warehouseId: number;
}

export function AlertsPanel({ warehouseId }: Props) {
  const { data: alerts, isLoading } = useAlerts(warehouseId);

  if (isLoading || !alerts) return null;

  if (alerts.length === 0) {
    return (
      <div className="flex items-center gap-3 rounded-xl border border-emerald-200 bg-emerald-50 px-6 py-4">
        <span className="text-xl">✓</span>
        <p className="text-sm font-medium text-emerald-800">
          All items are above their reorder threshold.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-red-200 bg-red-50">
      <div className="flex items-center gap-2 border-b border-red-200 px-6 py-4">
        <span className="text-xl">⚠</span>
        <h2 className="text-lg font-semibold text-red-900">
          {alerts.length} item{alerts.length === 1 ? "" : "s"} below reorder threshold
        </h2>
      </div>
      <ul className="divide-y divide-red-100">
        {alerts.map((item) => (
          <li key={item.item_id} className="flex items-center justify-between px-6 py-3">
            <span className="font-medium text-red-900">{item.sku}</span>
            <span className="text-sm text-red-700">
              {item.quantity_on_hand} on hand (threshold {item.reorder_threshold})
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
