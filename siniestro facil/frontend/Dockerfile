FROM node:22.20.0-alpine AS build
WORKDIR /app

ARG PUBLIC_API_BASE_URL
ARG PUBLIC_IDENTITY_CONFIG

COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN VITE_API_BASE_URL="${PUBLIC_API_BASE_URL}" \
    VITE_IDENTITY_PLATFORM_API_KEY="${PUBLIC_IDENTITY_CONFIG}" \
    npm run build

FROM nginxinc/nginx-unprivileged:1.29-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -qO- http://127.0.0.1:8080/health/live || exit 1
