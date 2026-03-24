# Multi-Stage Build für Produktion
FROM node:22-alpine AS builder

WORKDIR /app

# Dependencies installieren
COPY package*.json ./
RUN npm install

# Source-Code kopieren und bauen
COPY . .
RUN npm run build

# Production-Stage mit Nginx
FROM nginx:alpine

# Build-Output in Nginx kopieren
COPY --from=builder /app/dist /usr/share/nginx/html

# Nginx-Konfiguration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
