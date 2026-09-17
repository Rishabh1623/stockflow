import { type FormEvent, useState } from "react";
import { useCreateOrder, useInventory, useOrders, useUpdateOrderStatus } from "../lib/queries";
import type { InventoryItem, OrderCreate, OrderStatus } from "../lib/types";

const STATUS_FILTERS: Array<{ label: string; value: OrderStatus | undefined }> = [
  { label: "All", value: undefined },
  { label: "Pending", value: "pending" },
  { label: "Fulfilled", value: "fulfilled" },
  { label: "Shipped", value: "shipped" },
  { label: "Cancelled", value: "cancelled" },
];

// Mirrors ALLOWED_TRANSITIONS in app/services/orders.py — a UX nicety so we
// only show buttons for legal moves. The backend remains the authority: it
// still rejects anything invalid with a 409 regardless of what this shows.
const NEXT_STATUSES: Record<OrderStatus, OrderStatus[]> = {
  pending: ["fulfilled", "cancelled"],
  fulfilled: ["shipped"],
  shipped: [],
  cancelled: [],
};

const STATUS_STYLES: Record<OrderStatus, string> = {
  pending: "bg-amber-100 text-amber-700",
  fulfilled: "bg-blue-100 text-blue-700",
  shipped: "bg-emerald-100 text-emerald-700",
  cancelled: "bg-slate-200 text-slate-600",
};

interface Props {
  warehouseId: number;
}

export function OrdersPanel({ warehouseId }: Props) {
  const [statusFilter, setStatusFilter] = useState<OrderStatus | undefined>(undefined);
  const { data: orders, isLoading, isError } = useOrders(warehouseId, statusFilter);
  const { data: inventory } = useInventory(warehouseId);
  const createOrder = useCreateOrder(warehouseId);
  const updateStatus = useUpdateOrderStatus(warehouseId);

  const skuByItemId = new Map((inventory ?? []).map((item) => [item.item_id, item.sku]));

  return (
    <section className="rounded-xl border border-slate-200 bg-white">
      <div className="flex flex-col gap-4 border-b border-slate-200 px-6 py-4 sm:flex-row sm:items-center sm:justify-between">
        <h2 className="text-lg font-semibold text-slate-900">Orders</h2>
        <div className="flex flex-wrap gap-1 rounded-lg bg-slate-100 p-1">
          {STATUS_FILTERS.map((filter) => (
            <button
              key={filter.label}
              type="button"
              onClick={() => setStatusFilter(filter.value)}
              className={`rounded-md px-3 py-1 text-xs font-medium transition-colors ${
                statusFilter === filter.value
                  ? "bg-white text-slate-900 shadow-sm"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              {filter.label}
            </button>
          ))}
        </div>
      </div>

      <CreateOrderForm
        warehouseId={warehouseId}
        inventory={inventory ?? []}
        onCreate={(data) => createOrder.mutate(data)}
        isSubmitting={createOrder.isPending}
      />
      {createOrder.isError && (
        <p className="border-b border-red-100 bg-red-50 px-6 py-2 text-sm text-red-700">
          {createOrder.error.message}
        </p>
      )}

      {isLoading && <p className="px-6 py-8 text-sm text-slate-500">Loading orders…</p>}
      {isError && <p className="px-6 py-8 text-sm text-red-600">Failed to load orders.</p>}
      {orders && orders.length === 0 && (
        <p className="px-6 py-8 text-sm text-slate-500">No orders match this filter.</p>
      )}

      {orders && orders.length > 0 && (
        <ul className="divide-y divide-slate-100">
          {orders.map((order) => (
            <li
              key={order.order_id}
              className="flex flex-col gap-2 px-6 py-4 sm:flex-row sm:items-center sm:justify-between"
            >
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-medium text-slate-900">Order #{order.order_id}</span>
                  <span
                    className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${STATUS_STYLES[order.status]}`}
                  >
                    {order.status}
                  </span>
                </div>
                <p className="text-sm text-slate-500">
                  {order.customer_ref} ·{" "}
                  {order.items
                    .map((line) => `${skuByItemId.get(line.item_id) ?? `#${line.item_id}`} ×${line.quantity}`)
                    .join(", ")}
                </p>
              </div>
              <div className="flex gap-2">
                {NEXT_STATUSES[order.status].map((next) => (
                  <button
                    key={next}
                    type="button"
                    disabled={updateStatus.isPending}
                    onClick={() => updateStatus.mutate({ orderId: order.order_id, status: next })}
                    className="rounded-md border border-slate-300 px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
                  >
                    Mark {next}
                  </button>
                ))}
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

interface CreateOrderFormProps {
  warehouseId: number;
  inventory: InventoryItem[];
  onCreate: (data: OrderCreate) => void;
  isSubmitting: boolean;
}

function CreateOrderForm({ warehouseId, inventory, onCreate, isSubmitting }: CreateOrderFormProps) {
  const [customerRef, setCustomerRef] = useState("");
  const [itemId, setItemId] = useState<number | "">("");
  const [quantity, setQuantity] = useState(1);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!customerRef || itemId === "" || quantity <= 0) return;
    onCreate({
      warehouse_id: warehouseId,
      customer_ref: customerRef,
      items: [{ item_id: itemId, quantity }],
    });
    setCustomerRef("");
    setItemId("");
    setQuantity(1);
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-wrap items-end gap-3 border-b border-slate-200 bg-slate-50 px-6 py-4"
    >
      <div className="flex flex-col gap-1">
        <label className="text-xs font-medium text-slate-600" htmlFor="customer-ref">
          Customer
        </label>
        <input
          id="customer-ref"
          type="text"
          value={customerRef}
          onChange={(e) => setCustomerRef(e.target.value)}
          placeholder="cust-123"
          required
          className="rounded-md border border-slate-300 px-2.5 py-1.5 text-sm"
        />
      </div>
      <div className="flex flex-col gap-1">
        <label className="text-xs font-medium text-slate-600" htmlFor="item">
          SKU
        </label>
        <select
          id="item"
          value={itemId}
          onChange={(e) => setItemId(e.target.value ? Number(e.target.value) : "")}
          required
          className="rounded-md border border-slate-300 px-2.5 py-1.5 text-sm"
        >
          <option value="">Select…</option>
          {inventory.map((item) => (
            <option key={item.item_id} value={item.item_id}>
              {item.sku} ({item.quantity_on_hand} on hand)
            </option>
          ))}
        </select>
      </div>
      <div className="flex flex-col gap-1">
        <label className="text-xs font-medium text-slate-600" htmlFor="quantity">
          Qty
        </label>
        <input
          id="quantity"
          type="number"
          min={1}
          value={quantity}
          onChange={(e) => setQuantity(Number(e.target.value))}
          required
          className="w-20 rounded-md border border-slate-300 px-2.5 py-1.5 text-sm"
        />
      </div>
      <button
        type="submit"
        disabled={isSubmitting}
        className="rounded-md bg-slate-900 px-4 py-1.5 text-sm font-medium text-white hover:bg-slate-700 disabled:opacity-50"
      >
        {isSubmitting ? "Creating…" : "Create order"}
      </button>
    </form>
  );
}
