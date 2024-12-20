def progreso(index, total, mensaje_adicional=""):
    progreso = int((index / total) * 100)
    barra = '█' * (progreso // 2) + '-' * (50 - progreso // 2)  # 50 caracteres en la barra
    mensaje = f"🔄 Verificando tarjeta {index + 1}/{total}:\n[{barra}] {progreso}% {mensaje_adicional}"