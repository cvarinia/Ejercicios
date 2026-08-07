# evaluacion_compra.py
# Programa integrador: calcula el total de una compra con descuentos

# -- Entrada de datos ---------------------------------------------------------
precio_unitario = float(input("Ingrese el precio unitario: "))
cantidad        = int(input("Ingrese la cantidad: "))
respuesta       = input("¿Es cliente frecuente? (si/no): ")

# Normalizamos la respuesta: aceptamos "si", "sí" o "s"
# .strip() elimina espacios al inicio/fin, .lower() convierte a minúsculas
cliente_frecuente = respuesta.strip().lower() in ("si", "sí", "s")

# -- Cálculo del total bruto --------------------------------------------------
total_bruto = precio_unitario * cantidad

# -- Descuento con expresión anidada ------------------------------------------
# Regla 1: cantidad > 10                          →  10% de descuento
# Regla 2: es cliente frecuente (cantidad <= 10)  →   5% de descuento
# Regla 3: ninguna de las anteriores              →   sin descuento
porcentaje_descuento = 0.10 if cantidad > 10 else (0.05 if cliente_frecuente else 0)

# -- Cálculo del monto de descuento y total neto ------------------------------
monto_descuento = total_bruto * porcentaje_descuento
total_neto      = total_bruto - monto_descuento

# -- Mensajes de salida -------------------------------------------------------
pct = int(porcentaje_descuento * 100)
print(f"Total bruto: {total_bruto}")
print(f"Porcentaje y monto del descuento aplicado: {pct}% ({monto_descuento})")
print(f"Total neto a pagar: {total_neto}")
