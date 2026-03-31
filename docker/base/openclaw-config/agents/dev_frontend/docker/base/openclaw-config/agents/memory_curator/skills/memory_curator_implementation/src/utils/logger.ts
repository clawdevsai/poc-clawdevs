export interface LogEntry {
  timestamp: string;
  level: "debug" | "info" | "warn" | "error";
  context: string;
  message: string;
  data?: Record<string, any>;
}

export class Logger {
  constructor(private context: string) {}
  debug(message: string, data?: Record<string, any>) { this.log("debug", message, data); }
  info(message: string, data?: Record<string, any>) { this.log("info", message, data); }
  warn(message: string, data?: Record<string, any>) { this.log("warn", message, data); }
  error(message: string, data?: Record<string, any>) { this.log("error", message, data); }
  private log(level: any, message: string, data?: any) {
    const entry: LogEntry = { timestamp: new Date().toISOString(), level, context: this.context, message, data };
    console.log(JSON.stringify(entry));
  }
}
