import client from "./client";
import { HistoryItem } from "../types";

export const publishMessage = (topic: string, message: string) =>
  client.post("/publish", { topic, message });

export const getHistory = () =>
  client.get<HistoryItem[]>("/history");

export const clearHistory = () =>
  client.delete("/history");

export const exportPerfExcel = (results: object) =>
  client.post("/perf/export/excel", results, { responseType: "blob" });

// old component imports
export const publish = publishMessage;