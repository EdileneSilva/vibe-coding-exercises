FROM node:20-slim AS builder

WORKDIR /app

# Copy package files
COPY package.json ./

# Install dependencies
RUN npm install -g bun && \
    bun install

# Copy source files
COPY playwright.config.ts ./
COPY tests/ ./tests/

# Install Playwright browsers
RUN bunx playwright install --with-deps

FROM builder AS runner

WORKDIR /app

# Run tests
CMD ["bun", "run", "test"]
