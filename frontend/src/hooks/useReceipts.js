import { useCallback, useEffect, useState } from "react";
import { receiptApi } from "../api/receipts";

/**
 * 영수증 목록 데이터 페칭 훅.
 * 2주차 이후 실제 API 연동 시 로직 확장 예정.
 */
export function useReceipts(params = {}) {
  const [data, setData] = useState({ items: [], total: 0, page: 1, size: 20, pages: 0 });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchReceipts = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await receiptApi.list(params);
      setData(res.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [JSON.stringify(params)]);

  useEffect(() => {
    fetchReceipts();
  }, [fetchReceipts]);

  return { data, loading, error, refetch: fetchReceipts };
}

/**
 * 단일 영수증 상세 데이터 페칭 훅.
 */
export function useReceipt(id) {
  const [receipt, setReceipt] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchReceipt = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const res = await receiptApi.get(id);
      setReceipt(res.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchReceipt();
  }, [fetchReceipt]);

  return { receipt, loading, error, refetch: fetchReceipt };
}
