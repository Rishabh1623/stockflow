import { useParams } from "react-router-dom";
import { AlertsPanel } from "../components/AlertsPanel";
import { InventoryTable } from "../components/InventoryTable";
import { OrdersPanel } from "../components/OrdersPanel";

export function Dashboard() {
  const { warehouseId } = useParams();
  const id = Number(warehouseId);

  return (
    <div className="space-y-8">
      <AlertsPanel warehouseId={id} />
      <InventoryTable warehouseId={id} />
      <OrdersPanel warehouseId={id} />
    </div>
  );
}
