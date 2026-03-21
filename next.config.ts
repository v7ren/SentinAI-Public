import type { NextConfig } from "next";
import path from "path";
const projectRoot = path.resolve(__dirname);
const nextConfig: NextConfig = {
    reactCompiler: true,
    turbopack: {
        root: projectRoot,
        resolveAlias: {
            tailwindcss: path.join(projectRoot, "node_modules", "tailwindcss"),
            "@tailwindcss/postcss": path.join(projectRoot, "node_modules", "@tailwindcss", "postcss"),
        },
    },
    webpack: (config) => {
        config.context = projectRoot;
        config.resolve = config.resolve ?? {};
        config.resolve.modules = [
            path.join(projectRoot, "node_modules"),
            ...(Array.isArray(config.resolve.modules) ? config.resolve.modules : ["node_modules"]),
        ];
        config.resolve.alias = {
            ...config.resolve.alias,
            tailwindcss: path.join(projectRoot, "node_modules", "tailwindcss"),
            "@tailwindcss/postcss": path.join(projectRoot, "node_modules", "@tailwindcss", "postcss"),
        };
        return config;
    },
};
export default nextConfig;
