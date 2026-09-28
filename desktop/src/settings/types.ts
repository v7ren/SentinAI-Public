export type AppSettings = {
  gatewayUrl: string;
  engineUrl: string;
  opencodeBridgeUrl: string;
  opencodeApiKey: string;
  closesourceApiKey: string;
  workerSecret: string;
  scanModel: string;
};

export const defaultSettings: AppSettings = {
  gatewayUrl: "http://127.0.0.1:5001",
  engineUrl: "http://127.0.0.1:5002",
  opencodeBridgeUrl: "http://127.0.0.1:5010",
  opencodeApiKey: "",
  closesourceApiKey: "",
  workerSecret: "",
  scanModel: "deepseek-v4.1-flash",
};
