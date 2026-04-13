import axiosClient from "./axiosClient";

export const categoryApi = {
  /** 카테고리 목록 조회 */
  list() {
    return axiosClient.get("/api/categories");
  },
};
