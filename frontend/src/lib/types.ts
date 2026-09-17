// Mirrors app/schemas/*.py on the backend — kept in sync by hand since this
// is a small API surface; a generated client would be the move at a larger scale.

export interface Warehouse {
  warehouse_id: number;
  name: string;
  region: string;
}

export interface InventoryItem {
  item_id: number;
  warehouse_id: number;
  sku: string;
  quantity_on_hand: number;
  reorder_threshold: number;
  last_updated: string;
}

export type OrderStatus = "pending" | "fulfilled" | "shipped" | "cancelled";

export interface OrderItem {
  order_item_id: number;
  item_id: number;
  quantity: number;
}

export interface Order {
  order_id: number;
  warehouse_id: number;
  customer_ref: string;
  status: OrderStatus;
  created_at: string;
  updated_at: string;
  items: OrderItem[];
}

export interface OrderItemCreate {
  item_id: number;
  quantity: number;
}

export interface OrderCreate {
  warehouse_id: number;
  customer_ref: string;
  items: OrderItemCreate[];
}
