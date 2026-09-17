import { Link, useParams } from "react-router-dom";
import { useWarehouses } from "../lib/queries";

export function WarehouseSelector() {
  const { warehouseId } = useParams();
  const { data: warehouses, isLoading } = useWarehouses();

  if (isLoading || !warehouses?.length) return null;

  return (
    <nav className="flex gap-1 rounded-lg bg-slate-100 p-1">
      {warehouses.map((w) => {
        const isActive = String(w.warehouse_id) === warehouseId;
        return (
          <Link
            key={w.warehouse_id}
            to={`/warehouses/${w.warehouse_id}`}
            className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
              isActive ? "bg-white text-slate-900 shadow-sm" : "text-slate-600 hover:text-slate-900"
            }`}
          >
            {w.name}
          </Link>
        );
      })}
    </nav>
  );
}
