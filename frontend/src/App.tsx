import React, { useState } from 'react';
import {BrowserRouter as Router, Route, Routes} from 'react-router-dom';
import './App.css';
import Login from './Login/login';
import Register from './Register/register';
import Chat from './chat/chat';
import { AuthTokenContext } from './AuthTokenContext'; // Import the AuthTokenContext

function App() {
 const [authToken, setAuthToken] = useState<string | null>(null);

  return (
    <Router>
      <div className="App">
        <AuthTokenContext.Provider value={[authToken, setAuthToken]}>
          <Routes>
            <Route path="/login" element={<Login setAuthToken={setAuthToken}/>}/>
            <Route path="/register" element={<Register setAuthToken={setAuthToken}/>}/>
            <Route path="/chat" element={<Chat/>}/>
            <Route path="*" element={<Login setAuthToken={setAuthToken}/>}/>
          </Routes>
        </AuthTokenContext.Provider>
      </div>
    </Router>
  );
}

export default App;