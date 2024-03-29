import React, {useState, useEffect, useContext} from 'react';
import axios from 'axios';
import { AuthTokenContext } from '../AuthTokenContext'; // Import the AuthTokenContext

interface Session {
  id: number;
  name: string;
  // include other properties here that a session might have
}
function Chat() {
  const authToken = useContext(AuthTokenContext);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [models, setModels] = useState<string[]>([]);
  const [selectedModel, setSelectedModel] = useState("gemma:7b");
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');

  useEffect(() => {
    // Fetch sessions and models when the component mounts
    axios.get('/session', { headers: { Authorization: `Bearer ${authToken}` } })
      .then(response => setSessions(response.data))
      .catch(error => console.error(error));

    axios.get('/models', { headers: { Authorization: `Bearer ${authToken}` } })
      .then(response => setModels(response.data))
      .catch(error => console.error(error));
  }, [authToken]);

  const handleNewChat = () => {
    // Implement the functionality to create a new chat session
  };

  const handleSendMessage = () => {
    // Implement the functionality to send a message
  };

  return (
    <div style={{ display: 'flex' }}>
      <div style={{ width: '30%', overflowY: 'scroll' }}>
        <button onClick={handleNewChat}>New Chat</button>
        <button>Plugin</button>
        {sessions.map(session => (
          <div key={session.id}>{session.name}</div>
        ))}
      </div>
      <div style={{ width: '70%', overflowY: 'scroll', paddingBottom: '50px' }}>
        {messages.map((message, index) => (
          <div key={index}>{message}</div>
        ))}
      </div>
      <div style={{ width: '70%', position: 'fixed', bottom: '0', display: 'flex', flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' }}>
        <select value={selectedModel} onChange={e => setSelectedModel(e.target.value)}>
          {models.map(model => (
            <option key={model} value={model}>{model}</option>
          ))}
        </select>
        <input value={newMessage} onChange={e => setNewMessage(e.target.value)} />
        <button onClick={handleSendMessage}>Send</button>
      </div>
    </div>
  );
}

export default Chat;