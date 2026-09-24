import type { WebSocket } from "ws";

const clients = new Set<WebSocket>();

export function addRealtimeClient(client: WebSocket) {
  clients.add(client);
  client.on("close", () => clients.delete(client));
  client.on("error", () => clients.delete(client));
}

export function broadcastRealtime(event: string, payload: unknown) {
  const message = JSON.stringify({ event, payload, at: new Date().toISOString() });
  for (const client of clients) {
    if (client.readyState === 1) client.send(message);
  }
}