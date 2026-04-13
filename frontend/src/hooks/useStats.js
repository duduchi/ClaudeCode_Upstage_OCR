import { useCallback, useEffect, useState } from "react";
import { statsApi } from "../api/stats";

/**
 * 지출 통계 데이터 페칭 훅.
 * 2주차 이후 실제 API 연동 시 로직 확장 예정.
 */
export function useStats(params = {}) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchStats = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await statsApi.summary(params);
      setData(res.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [JSON.stringify(params)]);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  return { data, loading, error, refetch: fetchStats };
}
