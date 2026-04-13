import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import AppLayout from "./components/layout/AppLayout";
import Dashboard from "./pages/Dashboard";
import ReceiptDetail from "./pages/ReceiptDetail";
import ReceiptList from "./pages/ReceiptList";
import StatsPage from "./pages/StatsPage";
import UploadPage from "./pages/UploadPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="upload" element={<UploadPage />} />
          <Route path="receipts" element={<ReceiptList />} />
          <Route path="receipts/:id" element={<ReceiptDetail />} />
          <Route path="stats" element={<StatsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
