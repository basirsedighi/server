const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 8081 });
  
wss.on('connection', ws => {
  onConnection(ws);
  ws.on('message', message => {
    onMessage(message, ws);
  });
  ws.on('error', error => {
    OnError(error);
  });
   ws.on('close', ws=> {
    onClose();
})
});