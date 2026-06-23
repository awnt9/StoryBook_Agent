let refreshRequest = null;

function getAccessToken() {
  return localStorage.getItem("access_token");
}

async function refreshAccessToken() {
  if (!refreshRequest) {
    refreshRequest = fetch("/api/v1/auth/refresh", {
      method: "POST",
      credentials: "include",
    })
      .then(async (response) => {
        if (!response.ok) throw new Error("Tu sesión ha caducado. Vuelve a iniciar sesión.");

        const payload = await response.json();
        localStorage.setItem("access_token", payload.access_token);
        return payload.access_token;
      })
      .finally(() => {
        refreshRequest = null;
      });
  }

  return refreshRequest;
}

function buildHeaders(options, accessToken) {
  return {
    ...(options.body ? { "Content-Type": "application/json" } : {}),
    ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
    ...options.headers,
  };
}

async function parseResponse(response) {
  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new Error(payload?.detail || "No se pudo completar la operación");
  }

  return response.status === 204 ? null : response.json();
}

export async function apiRequest(path, options = {}) {
  const requestOptions = {
    ...options,
    credentials: "include",
    headers: buildHeaders(options, getAccessToken()),
  };

  let response = await fetch(path, requestOptions);

  if (response.status === 401) {
    try {
      const accessToken = await refreshAccessToken();
      response = await fetch(path, {
        ...requestOptions,
        headers: buildHeaders(options, accessToken),
      });
    } catch (error) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("user");
      throw error;
    }
  }

  return parseResponse(response);
}
