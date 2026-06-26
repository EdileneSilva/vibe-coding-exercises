import { defineConfig } from 'vitest/config';
import { fileURLToPath } from 'node:url';

export default defineConfig({
    resolve: {
        alias: {
            '$env/dynamic/public': fileURLToPath(new URL('./tests/mocks/env-public.ts', import.meta.url)),
            $lib: fileURLToPath(new URL('./src/lib', import.meta.url))
        }
    },
    test: {
        include: ['src/**/*.test.ts', 'tests/**/*.test.ts'],
        environment: 'node',
        coverage: {
            provider: 'v8',
            reporter: ['text', 'json', 'html'],
            reportsDirectory: './coverage'
        }
    }
});