import axiosClient from "./axiosClient";

export const receiptApi = {
  /** 영수증 업로드 및 OCR 분석 */
  upload(file, onUploadProgress) {
    const formData = new FormData();
    formData.append("file", file);
    return axiosClient.post("/api/receipts/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress,
    });
  },

  /** 목록 조회 */
  list(params = {}) {
    return axiosClient.get("/api/receipts", { params });
  },

  /** 상세 조회 */
  get(id) {
    return axiosClient.get(`/api/receipts/${id}`);
  },

  /** 수정 */
  update(id, data) {
    return axiosClient.put(`/api/receipts/${id}`, data);
  },

  /** 삭제 */
  remove(id) {
    return axiosClient.delete(`/api/receipts/${id}`);
  },
};
