/**
 * Proxy route handler that forwards API requests to the backend
 * This handles /api/* requests and forwards them to the backend server
 */

const BACKEND_URL = process.env.BACKEND_URL ?? "http://clawdevs-panel-backend:8000";

export async function GET(
  request: Request,
  { params }: { params: Promise<{ slug: string[] }> }
) {
  const { slug } = await params;
  const path = "api/" + slug.join("/");
  const url = new URL(request.url);
  const queryString = url.search;
  const backendUrl = `${BACKEND_URL}/${path}${queryString}`;

  try {
    const response = await fetch(backendUrl, {
      method: "GET",
      headers: {
        Accept: request.headers.get("accept") || "*/*",
        "Content-Type": request.headers.get("content-type") || "application/json",
      },
    });

    const data = await response.json();
    return Response.json(data, { status: response.status });
  } catch (error) {
    console.error(`Error proxying GET ${backendUrl}:`, error);
    return Response.json(
      { error: "Failed to fetch from backend" },
      { status: 502 }
    );
  }
}

export async function POST(
  request: Request,
  { params }: { params: Promise<{ slug: string[] }> }
) {
  const { slug } = await params;
  const path = "api/" + slug.join("/");
  const url = new URL(request.url);
  const queryString = url.search;
  const backendUrl = `${BACKEND_URL}/${path}${queryString}`;

  try {
    const body = await request.text();
    const response = await fetch(backendUrl, {
      method: "POST",
      headers: {
        Accept: request.headers.get("accept") || "*/*",
        "Content-Type": request.headers.get("content-type") || "application/json",
      },
      body: body ? body : undefined,
    });

    const data = await response.json();
    return Response.json(data, { status: response.status });
  } catch (error) {
    console.error(`Error proxying POST ${backendUrl}:`, error);
    return Response.json(
      { error: "Failed to fetch from backend" },
      { status: 502 }
    );
  }
}

export async function PUT(
  request: Request,
  { params }: { params: Promise<{ slug: string[] }> }
) {
  const { slug } = await params;
  const path = "api/" + slug.join("/");
  const url = new URL(request.url);
  const queryString = url.search;
  const backendUrl = `${BACKEND_URL}/${path}${queryString}`;

  try {
    const body = await request.text();
    const response = await fetch(backendUrl, {
      method: "PUT",
      headers: {
        Accept: request.headers.get("accept") || "*/*",
        "Content-Type": request.headers.get("content-type") || "application/json",
      },
      body: body ? body : undefined,
    });

    const data = await response.json();
    return Response.json(data, { status: response.status });
  } catch (error) {
    console.error(`Error proxying PUT ${backendUrl}:`, error);
    return Response.json(
      { error: "Failed to fetch from backend" },
      { status: 502 }
    );
  }
}

export async function DELETE(
  request: Request,
  { params }: { params: Promise<{ slug: string[] }> }
) {
  const { slug } = await params;
  const path = "api/" + slug.join("/");
  const url = new URL(request.url);
  const queryString = url.search;
  const backendUrl = `${BACKEND_URL}/${path}${queryString}`;

  try {
    const response = await fetch(backendUrl, {
      method: "DELETE",
      headers: {
        Accept: request.headers.get("accept") || "*/*",
        "Content-Type": request.headers.get("content-type") || "application/json",
      },
    });

    const data = await response.json();
    return Response.json(data, { status: response.status });
  } catch (error) {
    console.error(`Error proxying DELETE ${backendUrl}:`, error);
    return Response.json(
      { error: "Failed to fetch from backend" },
      { status: 502 }
    );
  }
}
