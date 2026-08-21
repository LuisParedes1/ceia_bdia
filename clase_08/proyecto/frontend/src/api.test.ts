import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { apiErrorMessage, createMember, getSession } from "./api";

beforeEach(() => {
  document.cookie = "csrf_token=token; path=/";
});
afterEach(() => {
  vi.restoreAllMocks();
});
describe("cookie API client", () => {
  it("sends cookies and CSRF for mutations", async () => {
    const fetcher = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(new Response("{}", { status: 201 }));
    await createMember("member@example.test", "viewer");
    expect(fetcher).toHaveBeenCalledWith(
      "/api/members",
      expect.objectContaining({
        credentials: "include",
        headers: expect.objectContaining({ "x-csrf-token": "token" }),
      }),
    );
  });
  it("does not attach CSRF to session reads", async () => {
    const fetcher = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(new Response(JSON.stringify({}), { status: 200 }));
    await getSession();
    expect(fetcher.mock.calls[0][1]?.headers).not.toHaveProperty(
      "x-csrf-token",
    );
  });

  it.each([
    [400, "La solicitud no es válida."],
    [401, "Se requiere autenticación."],
    [403, "No tenés permiso para realizar esta acción."],
    [404, "No se encontró el recurso solicitado."],
    [409, "No se pudo completar la solicitud por un conflicto."],
    [422, "Los datos enviados no son válidos."],
    [
      429,
      "Se realizaron demasiadas solicitudes. Intentá nuevamente más tarde.",
    ],
    [500, "Ocurrió un error interno. Intentá nuevamente más tarde."],
    [503, "Ocurrió un error interno. Intentá nuevamente más tarde."],
    [418, "No se pudo completar la solicitud."],
  ])("uses a Spanish fallback for HTTP %i", async (status, message) => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response("", { status, statusText: "Unauthorized" }),
    );
    await expect(getSession()).rejects.toThrow(message);
  });

  it("never exposes statusText for non-JSON failures", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response("<html>failure</html>", {
        status: 500,
        statusText: "Internal Server Error",
      }),
    );
    await expect(getSession()).rejects.toThrow(
      "Ocurrió un error interno. Intentá nuevamente más tarde.",
    );
  });

  it("normalizes legacy and structured validation errors without English leakage", () => {
    expect(apiErrorMessage("invalid credentials")).toBe(
      "El correo electrónico o la contraseña no son válidos.",
    );
    expect(apiErrorMessage("Se requiere autenticación.")).toBe(
      "Se requiere autenticación.",
    );
    expect(
      apiErrorMessage([
        {
          loc: ["body", "email"],
          type: "value_error",
          msg: "not a valid email",
        },
      ]),
    ).toBe("Ingresá un correo electrónico válido.");
    expect(
      apiErrorMessage([
        {
          loc: ["body", "password"],
          type: "string_too_short",
          msg: "String should have at least 8 characters",
        },
      ]),
    ).toBe("La contraseña debe tener al menos 8 caracteres.");
    expect(
      apiErrorMessage([
        { loc: ["body", "email"], type: "missing", msg: "Field required" },
      ]),
    ).toBe("Este campo es obligatorio.");
    expect(
      apiErrorMessage([
        {
          loc: ["body", "unknown"],
          type: "unexpected",
          msg: "English server exception",
        },
      ]),
    ).toBe("Los datos enviados no son válidos.");
  });

  it("uses the Spanish network failure", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValue(
      new TypeError("network unavailable"),
    );
    await expect(getSession()).rejects.toThrow("La API no está disponible.");
  });
});
