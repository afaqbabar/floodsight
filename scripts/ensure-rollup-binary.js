import { existsSync } from "node:fs";
import { execSync } from "node:child_process";
import path from "node:path";

const platform = process.platform;
const arch = process.arch;
const rollupBinaryPath = path.resolve(
  "node_modules",
  "@rollup",
  "rollup-linux-x64-gnu",
  "rollup.linux-x64-gnu.node",
);

const needsLinuxBinary = platform === "linux" && arch === "x64";

if (!needsLinuxBinary) {
  console.log(
    `ℹ️  Skipping Rollup native binary check for ${platform}/${arch}`,
  );
  process.exit(0);
}

if (existsSync(rollupBinaryPath)) {
  console.log("✅ Rollup native binary already present");
  process.exit(0);
}

console.log("⚠️ Rollup native binary missing, installing optional dependency...");

try {
  execSync("npm install --no-save @rollup/rollup-linux-x64-gnu", {
    stdio: "inherit",
  });
  console.log("✅ Rollup native binary installed successfully");
} catch (error) {
  console.warn(
    "⚠️ Failed to install Rollup native binary, build may fail on Linux runners",
    error?.message || error,
  );
}

