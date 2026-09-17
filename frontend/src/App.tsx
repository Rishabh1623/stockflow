import { Navigate, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { Dashboard } from "./pages/Dashboard";
import { WarehousesIndex } from "./pages/WarehousesIndex";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Navigate to="/warehouses" replace />} />
        <Route path="warehouses" element={<WarehousesIndex />} />
        <Route path="warehouses/:warehouseId" element={<Dashboard />} />
      </Route>
    </Routes>
  );
}

export default App;
