import axiosClient from "./axiosClient";

export const statsApi = {
  /** 통계 요약 조회 */
  summary(params = {}) {
    return axiosClient.get("/api/stats/summary", { params });
  },
};
