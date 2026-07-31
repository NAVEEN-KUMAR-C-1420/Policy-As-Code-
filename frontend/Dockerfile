# Stage 1: Build static assets
FROM node:20-alpine AS build-stage

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# Stage 2: Production static web server (Nginx)
FROM nginx:alpine AS production-stage

COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD wget -qO- http://172.0.0.1:80/healthz || exit 1

CMD ["nginx", "-g", "daemon off;"]
