/* 
 * Copyright (c) 2026 Diego Silva Morais <lukewaresoftwarehouse@gmail.com>
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

import Axios, {
  AxiosError,
  AxiosHeaders,
  type AxiosInstance,
  type AxiosRequestConfig,
} from "axios";
import { getApiBaseUrl } from "./api-base-url";

const API_TIMEOUT_MS = 10_000;

let apiClient: AxiosInstance | null = null;

function getApiClient(): AxiosInstance {
  if (apiClient) return apiClient;

  const client = Axios.create({
    baseURL: getApiBaseUrl(),
    timeout: API_TIMEOUT_MS,
  });

  client.interceptors.request.use((config) => {
    if (typeof window === "undefined") return config;
    const token = localStorage.getItem("panel_token");
    if (token) {
      const headers = AxiosHeaders.from(config.headers);
      headers.set("Authorization", `Bearer ${token}`);
      config.headers = headers;
    }
    return config;
  });

  client.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
      if (typeof window !== "undefined") {
        const status = error.response?.status;
        if (status === 401 || status === 403) {
          localStorage.removeItem("panel_token");
          if (window.location.pathname !== "/login") {
            window.location.href = "/login";
          }
        }
      }
      return Promise.reject(error);
    }
  );

  apiClient = client;
  return client;
}

export const customInstance = async <T>(
  config: AxiosRequestConfig
): Promise<T> => {
  const { data } = await getApiClient().request<T>(config);
  return data;
};
