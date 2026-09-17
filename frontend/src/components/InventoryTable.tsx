import { useInventory } from "../lib/queries";

interface Props {
  warehouseId: number;
}

export function InventoryTable({ warehouseId }: Props) {
  const { data: items, isLoading, isError } = useInventory(warehouseId);

  return (
    <section className="rounded-xl border border-slate-200 bg-white">
      <div className="border-b border-slate-200 px-6 py-4">
        <h2 className="text-lg font-semibold text-slate-900">Inventory</h2>
      </div>

      {isLoading && <p className="px-6 py-8 text-sm text-slate-500">Loading inventory…</p>}
      {isError && <p className="px-6 py-8 text-sm text-red-600">Failed to load inventory.</p>}

      {items && items.length === 0 && (
        <p className="px-6 py-8 text-sm text-slate-500">No inventory items for this warehouse.</p>
      )}

      {items && items.length > 0 && (
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
              <th className="px-6 py-3 font-medium">SKU</th>
              <th className="px-6 py-3 font-medium">Quantity on hand</th>
              <th className="px-6 py-3 font-medium">Reorder threshold</th>
              <th className="px-6 py-3 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => {
              const isLow = item.quantity_on_hand < item.reorder_threshold;
              return (
                <tr
                  key={item.item_id}
                  className={`border-b border-slate-100 last:border-0 ${isLow ? "bg-red-50" : ""}`}
                >
                  <td className="px-6 py-3 font-medium text-slate-900">{item.sku}</td>
                  <td className={`px-6 py-3 ${isLow ? "font-semibold text-red-700" : "text-slate-700"}`}>
                    {item.quantity_on_hand}
                  </td>
                  <td className="px-6 py-3 text-slate-500">{item.reorder_threshold}</td>
                  <td className="px-6 py-3">
                    {isLow ? (
                      <span className="inline-flex items-center rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-medium text-red-700">
                        Low stock
                      </span>
                    ) : (
                      <span className="inline-flex items-center rounded-full bg-emerald-100 px-2.5 py-0.5 text-xs font-medium text-emerald-700">
                        Healthy
                      </span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </section>
  );
}
