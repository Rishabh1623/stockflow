# syntax=docker/dockerfile:1

# ---- builder: install deps and produce the static production build ----
FROM node:20-slim AS builder

WORKDIR /app

# Dependency manifests first, same layer-caching reasoning as the backend
# Dockerfile (Stage 4): this layer only invalidates when dependencies
# actually change, not on every app-code edit.
COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Vite bakes VITE_* values into the compiled JS bundle at build time, not at
# container runtime — there's no env var to swap after the image is built.
# For now that means "the target backend URL" is a build-time decision
# (default here matches local dev); revisit with a runtime env-injection
# script if this needs to be configurable per-deployment without rebuilding.
ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build


# ---- runtime: nginx serving the static build, non-root ----
FROM nginx:1.27-alpine AS runtime

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

# nginx's default port 80 needs root or CAP_NET_BIND_SERVICE to bind; nginx.conf
# listens on 8080 instead specifically so this can run as the existing
# unprivileged `nginx` user — same non-root reasoning as the backend image.
RUN chown -R nginx:nginx /usr/share/nginx/html /var/cache/nginx /var/log/nginx /etc/nginx/conf.d \
    && touch /var/run/nginx.pid \
    && chown nginx:nginx /var/run/nginx.pid

USER nginx
EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
