import Axios, { type AxiosRequestConfig } from "axios";
import { getApiBaseUrl } from "./api-base-url";

export const customInstance = async <T>(
  config: AxiosRequestConfig
): Promise<T> => {
  const token =
    typeof window !== "undefined"
      ? localStorage.getItem("panel_token")
      : null;

  const { data } = await Axios({
    ...config,
    baseURL: getApiBaseUrl(),
    headers: {
      ...config.headers,
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
  return data;
};
