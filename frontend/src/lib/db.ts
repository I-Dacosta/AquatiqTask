import { Pool } from "pg";

declare global {
    // eslint-disable-next-line no-var
    var __PRIORITIAI_POOL__: Pool | undefined;
}

export function getPool(): Pool {
    if (!process.env.DATABASE_URL) {
        throw new Error("DATABASE_URL mangler. Sett den i miljøvariabler eller docker-compose.");
    }

    if (!globalThis.__PRIORITIAI_POOL__) {
        globalThis.__PRIORITIAI_POOL__ = new Pool({ connectionString: process.env.DATABASE_URL });
    }

    return globalThis.__PRIORITIAI_POOL__;
}

export default getPool;
