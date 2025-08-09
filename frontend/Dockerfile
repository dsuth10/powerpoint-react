# syntax=docker/dockerfile:1
FROM node:18.19.0 AS base
WORKDIR /app

# Install dependencies separately to leverage Docker layer caching
COPY package*.json ./
RUN npm ci

# Copy source
COPY . .

# Tools for healthchecks
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# ----- Development image -----
FROM base AS dev
ENV NODE_ENV=development
# Use non-root user for better security
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 5173
CMD ["npm", "run", "dev"]

# ----- Production build -----
FROM base AS build
ENV NODE_ENV=production
RUN npm run build

# ----- Production runtime -----
FROM node:18.19.0 AS prod
WORKDIR /app
ENV NODE_ENV=production
RUN useradd -m appuser && chown -R appuser:appuser /app
COPY --from=build /app/dist ./dist
COPY package*.json ./
RUN npm ci --omit=dev
USER appuser
EXPOSE 4173
CMD ["npx", "vite", "preview", "--host", "0.0.0.0", "--port", "4173"]