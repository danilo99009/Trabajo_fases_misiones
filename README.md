# Proyecto SRE — Fase 1

## Estructura
```
proyecto-sre/
├── app/
│   ├── app.py
│   ├── test_app.py
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
└── .github/workflows/deploy.yml
```

## 1. Security Groups en la instancia
Abre estos puertos en el Security Group de tu instancia (inbound rules):

| Puerto | Protocolo | Origen              | Para qué |
|--------|-----------|---------------------|----------|
| 22     | TCP       | Tu IP (no 0.0.0.0/0)| SSH |
| 80     | TCP       | 0.0.0.0/0            | HTTP (Let's Encrypt + redirección) |
| 443    | TCP       | 0.0.0.0/0            | HTTPS (API) |
| 81     | TCP       | Tu IP                | Panel admin de Nginx Proxy Manager |

No abras el 3306 (MySQL) ni el 5000 (Flask) al público: quedan solo en la red interna de Docker.

## 2. Preparar el servidor
```bash
sudo apt update && sudo apt install -y docker.io docker-compose-plugin
sudo usermod -aG docker $USER
# cierra sesión y vuelve a entrar para que aplique el grupo docker

git clone <tu-repo> proyecto-sre
cd proyecto-sre
cp .env.example .env
nano .env   # pon contraseñas reales, este archivo NO se sube a git
```

## 3. Levantar Flask + MySQL
```bash
docker compose up -d --build
docker compose ps
docker compose logs -f flask-api
```

## 4. Nginx Proxy Manager (NPM)
NPM no va en el docker-compose del proyecto porque es infraestructura compartida del host, no parte de la app. Créalo aparte:

```yaml
# nginx-proxy-manager/docker-compose.yml
services:
  npm:
    image: jc21/nginx-proxy-manager:latest
    container_name: npm
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
      - "81:81"
    volumes:
      - ./data:/data
      - ./letsencrypt:/etc/letsencrypt
    networks:
      - app-network

networks:
  app-network:
    external: true
    name: app-network
```
```bash
cd nginx-proxy-manager
docker compose up -d
```

Pasos en el panel (`http://IP_DE_TU_INSTANCIA:81`):
1. Login con las credenciales default (`admin@example.com` / `changeme`) y cámbialas.
2. **Hosts → Proxy Hosts → Add Proxy Host**.
3. Domain: tu subdominio DuckDNS (ej. `mi-api.duckdns.org`).
4. Forward Hostname/IP: `flask-api` (nombre del contenedor, ya está en `app-network`).
5. Forward Port: `5000`.
6. Pestaña **SSL** → Request a new SSL Certificate → Let's Encrypt → activa "Force SSL".

## 5. DuckDNS
1. Entra a duckdns.org, crea el subdominio (ej. `mi-api`).
2. Apunta el subdominio a la IP pública de tu instancia.
3. (Opcional pero recomendado) instala el script de actualización de IP de DuckDNS con un cron cada 5 min, por si la IP cambia.

## 6. Secrets en GitHub (para que `deploy.yml` funcione)
En tu repo: **Settings → Secrets and variables → Actions → New repository secret**:

- `SSH_HOST`: IP pública de la instancia
- `SSH_USER`: usuario SSH (ej. `ubuntu`)
- `SSH_PRIVATE_KEY`: contenido completo de tu `.pem`/clave privada

## Punto de control de la Fase 1
- `git push origin main` → el pipeline en Actions debe quedar en verde.
- `curl -I https://mi-api.duckdns.org/health` → debe responder `200 OK`.
