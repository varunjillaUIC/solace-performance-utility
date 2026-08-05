export const formatNumber = (n: number) => n.toLocaleString();

export const formatMs = (ms: number) => `${ms} ms`;

export const formatMsgPerSec = (n: number) => `${n.toLocaleString()} msg/s`;

export const formatBytes = (bytes: number): string => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

export const formatTime = (iso: string) =>
  new Date(iso).toLocaleTimeString();

export const formatDateTime = (iso: string) =>
  new Date(iso).toLocaleString();

export const avgOf = (arr: number[]): number =>
  arr.length ? Math.round(arr.reduce((a, b) => a + b, 0) / arr.length) : 0;

export const maxOf = (arr: number[]): number =>
  arr.length ? Math.max(...arr) : 0;