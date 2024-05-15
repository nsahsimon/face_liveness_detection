const WebSocket = require('ws');

// Create a WebSocket server
const wss = new WebSocket.Server({ port: 5000 });

// Event listener for when a client connects to the server
wss.on('connection', function connection(ws) {
  console.log('Client connected');

  // Event listener for messages received from the client
  ws.on('message', function incoming(message) {
    console.log('Received:', message);

    // Echo the message back to the client
    ws.send(`Echo: ${message}`);
  });

  // Event listener for when the client closes the connection
  ws.on('close', function close() {
    console.log('Client disconnected');
  });
});
