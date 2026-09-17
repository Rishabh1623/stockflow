import type { InventoryItem, Order, OrderCreate, OrderStatus, Warehouse } from "./types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL as string;

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const message =
      typeof body.detail === "string" ? body.detail : `Request failed with status ${response.status}`;
    throw new ApiError(response.status, message);
  }

  return response.json() as Promise<T>;
}

export const api = {
  listWarehouses: () => request<Warehouse[]>("/api/v1/warehouses"),

  listInventory: (warehouseId: number) => request<InventoryItem[]>(`/api/v1/inventory/${warehouseId}`),

  listAlerts: (warehouseId: number) =>
    request<InventoryItem[]>(`/api/v1/inventory/${warehouseId}/alerts`),

  listOrders: (warehouseId: number, status?: OrderStatus) => {
    const query = status ? `?status=${status}` : "";
    return request<Order[]>(`/api/v1/orders/${warehouseId}${query}`);
  },

  createOrder: (data: OrderCreate) =>
    request<Order>("/api/v1/orders", { method: "POST", body: JSON.stringify(data) }),

  updateOrderStatus: (orderId: number, status: OrderStatus) =>
    request<Order>(`/api/v1/orders/${orderId}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    }),
};
