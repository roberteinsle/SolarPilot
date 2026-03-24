FROM nginx:alpine

# Nginx-Konfiguration kopieren
COPY default.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
