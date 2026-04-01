// Copyright (c) 2026 Diego Silva Morais <lukewaresoftwarehouse@gmail.com>
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

/**
 * LogEntry - Represents a single log entry with timestamp and context
 * Used to track execution flow and debugging information throughout
 * the requirement parsing and hook execution lifecycle
 */
export interface LogEntry {
  /** Log level: debug < info < warn < error */
  level: 'debug' | 'info' | 'warn' | 'error';
  /** ISO timestamp when the log entry was created */
  timestamp: Date;
  /** Main log message */
  message: string;
  /** Optional structured data for additional context */
  data?: Record<string, any>;
}

/**
 * Logger - Structured logging service for tracking execution flow
 * Provides both console output and in-memory log storage for later retrieval
 * Used by all agents' before_execution hooks to track cascade parsing
 *
 * Example:
 * ```typescript
 * logger.info('Parsing requirements from conversation', { agentId: 'agent-123' });
 * const logs = logger.getLogs();
 * ```
 */
class Logger {
  /** In-memory storage of all log entries */
  private logs: LogEntry[] = [];

  /**
   * Log a message at a specific level
   * @param level The severity level of the log
   * @param message The main message to log
   * @param data Optional structured data to include
   */
  public log(level: 'debug' | 'info' | 'warn' | 'error', message: string, data?: Record<string, any>): void {
    const entry: LogEntry = {
      level,
      timestamp: new Date(),
      message,
      data,
    };

    this.logs.push(entry);

    // Output to console with appropriate formatting
    const prefix = `[${entry.timestamp.toISOString()}] [${level.toUpperCase()}]`;
    if (data) {
      console.log(`${prefix} ${message}`, data);
    } else {
      console.log(`${prefix} ${message}`);
    }
  }

  /**
   * Log a debug-level message
   * @param message The message to log
   * @param data Optional structured data
   */
  public debug(message: string, data?: Record<string, any>): void {
    this.log('debug', message, data);
  }

  /**
   * Log an info-level message
   * @param message The message to log
   * @param data Optional structured data
   */
  public info(message: string, data?: Record<string, any>): void {
    this.log('info', message, data);
  }

  /**
   * Log a warning-level message
   * @param message The message to log
   * @param data Optional structured data
   */
  public warn(message: string, data?: Record<string, any>): void {
    this.log('warn', message, data);
  }

  /**
   * Log an error-level message
   * @param message The message to log
   * @param data Optional structured data
   */
  public error(message: string, data?: Record<string, any>): void {
    this.log('error', message, data);
  }

  /**
   * Retrieve all accumulated log entries
   * Useful for exporting logs, debugging, or audit trails
   * @returns Array of all log entries in chronological order
   */
  public getLogs(): LogEntry[] {
    return [...this.logs];
  }

  /**
   * Clear all accumulated log entries
   * Use this between agent runs to isolate log contexts
   */
  public clear(): void {
    this.logs = [];
  }

  /**
   * Get logs filtered by level
   * @param level The level to filter by
   * @returns Array of log entries matching the level
   */
  public getLogsByLevel(level: 'debug' | 'info' | 'warn' | 'error'): LogEntry[] {
    return this.logs.filter(entry => entry.level === level);
  }

  /**
   * Get the total count of all logged entries
   * @returns Number of log entries
   */
  public getCount(): number {
    return this.logs.length;
  }
}

/**
 * Global logger singleton instance
 * All agents and hooks should use this shared instance
 * for consistent logging across the system
 */
export const logger = new Logger();

export default Logger;
