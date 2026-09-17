import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "./api";
import type { OrderCreate, OrderStatus } from "./types";

// Polling interval for "live-ish" dashboard reads. Shorter than the backend's
// 30s Redis cache TTL (Stage 3), so in steady state most of these requests
// are served from cache rather than hitting Postgres.
const POLL_INTERVAL_MS = 5000;

export function useWarehouses() {
  return useQuery({ queryKey: ["warehouses"], queryFn: api.listWarehouses });
}

export function useInventory(warehouseId: number) {
  return useQuery({
    queryKey: ["inventory", warehouseId],
    queryFn: () => api.listInventory(warehouseId),
    refetchInterval: POLL_INTERVAL_MS,
  });
}

export function useAlerts(warehouseId: number) {
  return useQuery({
    queryKey: ["alerts", warehouseId],
    queryFn: () => api.listAlerts(warehouseId),
    refetchInterval: POLL_INTERVAL_MS,
  });
}

export function useOrders(warehouseId: number, status?: OrderStatus) {
  return useQuery({
    queryKey: ["orders", warehouseId, status ?? "all"],
    queryFn: () => api.listOrders(warehouseId, status),
    refetchInterval: POLL_INTERVAL_MS,
  });
}

export function useCreateOrder(warehouseId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: OrderCreate) => api.createOrder(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["orders", warehouseId] });
    },
  });
}

export function useUpdateOrderStatus(warehouseId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ orderId, status }: { orderId: number; status: OrderStatus }) =>
      api.updateOrderStatus(orderId, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["orders", warehouseId] });
      queryClient.invalidateQueries({ queryKey: ["inventory", warehouseId] });
      queryClient.invalidateQueries({ queryKey: ["alerts", warehouseId] });
    },
  });
}
