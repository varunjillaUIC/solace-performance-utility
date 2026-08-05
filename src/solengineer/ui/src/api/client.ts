import axios from "axios";
import { API_BASE } from "../config/constants";

const client = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
  timeout: 30000,
});

export default client;