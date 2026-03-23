import { defineConfig } from "orval";

export default defineConfig({
  panel: {
    input: {
      target: "http://localhost:8000/openapi.json",
    },
    output: {
      mode: "tags-split",
      target: "src/lib/api",
      schemas: "src/lib/api/models",
      client: "react-query",
      override: {
        mutator: {
          path: "src/lib/axios-instance.ts",
          name: "customInstance",
        },
        query: {
          useQuery: true,
          useMutation: true,
        },
      },
    },
  },
});
