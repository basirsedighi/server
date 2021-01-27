const express = require('express');
const bodyParser = require('body-parser');
const http = require('http');
const socketIO = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = socketIO(server);

const port = 3000;

io.on('connection', socket => {
  console.log('client connected');

  socket.on('test', (message) => {
    console.log(message)
    let date = new Date()

    io.sockets.emit('test', {connectionStatus:true,timeStamp:date.toLocaleTimeString()});
    
  });


  socket.on('disconnect', () => {
    console.log(' disconnected');
  });
});

app.use(function (req, res, next) {
    res.header('Access-Control-Allow-Credentials', 'true');
    res.header("Access-Control-Allow-Origin", "http://localhost:4200");
    res.header('Access-Control-Allow-Methods', 'GET,PATCH,PUT,POST,DELETE');
    res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
    next();
  });
  
  app.use(bodyParser.json());

  server.listen(port, () => {
    console.log(`Started on port ${port}`);
  });
  
  module.exports = {app};