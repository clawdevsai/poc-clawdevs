import Axios, { type AxiosRequestConfig } from "axios";

const BACKEND_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const customInstance = async <T>(
  config: AxiosRequestConfig
): Promise<T> => {
  const token =
    typeof window !== "undefined"
      ? localStorage.getItem("panel_token")
      : null;

  const { data } = await Axios({
    ...config,
    baseURL: BACKEND_URL,
    headers: {
      ...config.headers,
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
  return data;
};
