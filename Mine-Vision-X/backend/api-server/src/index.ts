import app from "./app";
import { logger } from "./lib/logger";
import { createServer } from "node:http";
import { WebSocketServer } from "ws";
import { addRealtimeClient } from "./realtime/manager";

const rawPort = process.env["PORT"];

if (!rawPort) {
  throw new Error(
    "PORT environment variable is required but was not provided.",
  );
}

const port = Number(rawPort);

if (Number.isNaN(port) || port <= 0) {
  throw new Error(`Invalid PORT value: "${rawPort}"`);
}

const server = createServer(app);
const websocketServer = new WebSocketServer({ noServer: true });
websocketServer.on("connection", (socket) => addRealtimeClient(socket));
server.on("upgrade", (request, socket, head) => {
  if (request.url !== "/ws") {
    socket.destroy();
    return;
  }
  websocketServer.handleUpgrade(request, socket, head, (client) => {
    websocketServer.emit("connection", client, request);
  });
});

server.listen(port, () => {
  logger.info({ port }, "Server listening");
});
