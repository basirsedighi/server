const WebSocket = require('ws');
var net = require('net');
const wss = new WebSocket.Server({ port: 8081});
  
wss.on('connection', ws => {
  
  onConnection(ws)
  ws.on('message', message => {
    onMessage(message, ws);
  });
  ws.on('error', error => {
    OnError(error);
  });
   ws.on('close', ws=> {
    onClose();
    
})

function onClose(){
  console.log("connection closed")
}

function onConnection(ws){
console.log("connected")

wss.emit('message',"hello from server")

};

});

// var server = net.createServer();    
// server.on('connection', handleConnection);

// server.listen(9000, function() {    
//   console.log('server listening to %j', server.address());  
// });

// function handleConnection(conn) {    
//   var remoteAddress = conn.remoteAddress + ':' + conn.remotePort;  
//   console.log('new client connection from %s', remoteAddress);
// }