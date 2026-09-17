import { Outlet } from "react-router-dom";
import { WarehouseSelector } from "./WarehouseSelector";

export function Layout() {
  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl flex-col gap-4 px-6 py-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-xl font-semibold text-slate-900">StockFlow</h1>
            <p className="text-sm text-slate-500">Supply chain visibility</p>
          </div>
          <WarehouseSelector />
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-6 py-8">
        <Outlet />
      </main>
    </div>
  );
}
