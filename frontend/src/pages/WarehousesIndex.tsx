import { Navigate } from "react-router-dom";
import { useWarehouses } from "../lib/queries";

export function WarehousesIndex() {
  const { data: warehouses, isLoading, isError } = useWarehouses();

  if (isLoading) return <p className="text-slate-500">Loading warehouses…</p>;
  if (isError) return <p className="text-red-600">Failed to load warehouses.</p>;
  if (!warehouses || warehouses.length === 0) {
    return (
      <p className="text-slate-500">
        No warehouses yet — seed some data first (see scripts/seed.py on the backend).
      </p>
    );
  }

  return <Navigate to={`/warehouses/${warehouses[0].warehouse_id}`} replace />;
}
