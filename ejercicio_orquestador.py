"""
Ejercicio: Orquestador Concurrente de Modelos
=============================================
Simula un backend que consulta múltiples fuentes de IA de forma concurrente,
con control de flujo (Semaphore), manejo de timeouts y resiliencia ante fallos.

Requisitos: Python 3.12+
No se requieren dependencias externas.
"""

import asyncio
import time


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def log(msg: str) -> None:
    """Imprime un mensaje con timestamp relativo al inicio del programa."""
    elapsed = time.perf_counter() - START_TIME
    print(f"[{elapsed:5.2f}s] {msg}")


START_TIME = time.perf_counter()


# ---------------------------------------------------------------------------
# 1. Simulación de llamadas a modelos (I/O-bound con latencia de red simulada)
# ---------------------------------------------------------------------------

async def gpt_4_call(prompt: str) -> dict:
    """Simula una llamada a GPT-4 con ~1.5 s de latencia."""
    log("GPT-4      → iniciando llamada...")
    await asyncio.sleep(1.5)          # simula espera de red (NO bloquea el loop)
    log("GPT-4      ← respuesta recibida")
    return {"model": "gpt-4", "response": f"Respuesta GPT-4 para: '{prompt}'"}


async def claude_3_call(prompt: str) -> dict:
    """Simula una llamada a Claude 3 con ~0.8 s de latencia."""
    log("Claude-3   → iniciando llamada...")
    await asyncio.sleep(0.8)
    log("Claude-3   ← respuesta recibida")
    return {"model": "claude-3", "response": f"Respuesta Claude-3 para: '{prompt}'"}


async def local_llama_call(prompt: str) -> dict:
    """Simula una llamada a un LLaMA local con ~2.5 s de latencia.
    Esta superará el timeout de 2 s intencionalmente para demostrar la resiliencia."""
    log("LLaMA-local → iniciando llamada...")
    await asyncio.sleep(2.5)          # intencional: supera el timeout
    log("LLaMA-local ← respuesta recibida")  # esta línea nunca se alcanza
    return {"model": "llama-local", "response": f"Respuesta LLaMA para: '{prompt}'"}


# ---------------------------------------------------------------------------
# 2. Control de flujo con Semaphore
#    Solo 2 llamadas pueden ejecutarse simultáneamente, aunque lancemos 10.
# ---------------------------------------------------------------------------

async def throttled_model_call(
    coro_fn,          # la corrutina a ejecutar (gpt_4_call, etc.)
    prompt: str,
    sem: asyncio.Semaphore,
    call_id: int,
) -> dict:
    """
    Envuelve cualquier corrutina de modelo con:
      - control de concurrencia (Semaphore)
      - timeout individual de 2 segundos por llamada
    """
    async with sem:                           # el semáforo limita a N simultáneas
        log(f"[#{call_id}] Slot libre → ejecutando {coro_fn.__name__}")
        try:
            async with asyncio.timeout(2.0):  # corta si tarda más de 2 s
                result = await coro_fn(prompt)
                result["call_id"] = call_id
                return result
        except TimeoutError:
            log(f"[#{call_id}] ⚠ TIMEOUT en {coro_fn.__name__} — aplicando fallback")
            return {
                "call_id": call_id,
                "model": coro_fn.__name__,
                "error": "TimeoutError: la llamada superó 2 s",
                "response": None,
            }


# ---------------------------------------------------------------------------
# 3. Orquestador principal
# ---------------------------------------------------------------------------

async def orquestar_modelos(prompt: str) -> None:
    """
    Dispara 10 simulaciones de llamadas usando los 3 modelos,
    con un Semaphore(2) para limitar la concurrencia.
    """
    log("=" * 55)
    log(f"Prompt recibido: '{prompt}'")
    log("Lanzando 10 llamadas con Semaphore(2) — máx 2 en paralelo")
    log("=" * 55)

    # Rotamos entre los 3 modelos para generar 10 llamadas
    modelos = [gpt_4_call, claude_3_call, local_llama_call]
    sem = asyncio.Semaphore(2)

    tareas = [
        throttled_model_call(modelos[i % len(modelos)], prompt, sem, call_id=i + 1)
        for i in range(10)
    ]

    # gather dispara todas las tareas; return_exceptions=True evita que un
    # fallo individual tumbe el lote completo.
    resultados = await asyncio.gather(*tareas, return_exceptions=True)

    # --- Resumen ---
    log("=" * 55)
    log("RESULTADOS")
    log("=" * 55)
    exitosos = []
    fallidos = []

    for r in resultados:
        if isinstance(r, Exception):
            # Excepción inesperada no capturada dentro de throttled_model_call
            fallidos.append({"error": str(r)})
        elif r.get("error"):
            fallidos.append(r)
        else:
            exitosos.append(r)

    print(f"\n  ✓ Exitosos : {len(exitosos)}/{len(tareas)}")
    for r in exitosos:
        print(f"    [#{r['call_id']}] {r['model']}: {r['response']}")

    print(f"\n  ✗ Fallidos : {len(fallidos)}/{len(tareas)}")
    for r in fallidos:
        print(f"    [#{r.get('call_id', '?')}] {r.get('model', '?')}: {r['error']}")

    print()


# ---------------------------------------------------------------------------
# 4. Punto de entrada moderno (Python 3.12)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    asyncio.run(orquestar_modelos("¿Cuál es el mejor framework de ML en 2025?"))
