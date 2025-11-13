# 🐳 Guía Completa de Docker

## 📋 Resumen

Este proyecto usa un **Dockerfile multi-stage** que:
1. **Stage 1 (Node.js)**: Compila el frontend Vue → `web/dist/`
2. **Stage 2 (Python)**: Copia el frontend compilado y ejecuta FastAPI

**Resultado**: Un único contenedor con backend + frontend en el puerto 8080.

---

## 🚀 Comandos Básicos

### Build y Arranque

```powershell
# Opción 1: Build + Start en un comando
docker-compose up --build

# Opción 2: Build separado
docker-compose build
docker-compose up

# Opción 3: En background (detached)
docker-compose up -d
```

### Ver Logs

```powershell
# Logs en tiempo real
docker-compose logs -f

# Últimas 100 líneas
docker-compose logs --tail=100

# Logs de un servicio específico
# Documentos auxiliares archivados

Este archivo se ha archivado para evitar duplicación con `README.md` y `DEPLOYMENT.md`.

Consulta `README.md` para la documentación principal del proyecto y `DEPLOYMENT.md` para la guía de despliegue en producción.

Si necesitas recuperar información de este archivo, revisa el historial de Git.
docker-compose down
