import React, { useState } from "react";
import "./register.css";
import { FaUserAlt } from "react-icons/fa";
import { FaLock } from "react-icons/fa";

function Register({ setAuthToken }: { setAuthToken: (token: string) => void }) {
  // rest of your code

    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [api_key, setAPI] = useState("")
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        const response = await fetch('http://localhost:8000/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        });

        const data = await response.json();

        if (!data.api) {
            setError(data.detail);
        } else {
            setAPI(data.api);

            // Handle successful login
        }
    }

    return (
    <div className="wrapper">
        <form onSubmit={handleSubmit}>
            <h1>Create your account</h1>
            <div className="input-box">
                <FaUserAlt className="icon"/>
                <input type="text" placeholder="Username" required maxLength={64} value={username} onChange={(e) => {setUsername(e.target.value); setError("");}}/>
            </div>
            <div className="input-box">
                <FaLock className="icon"/>
                <input type="password" placeholder="Password" required value={password} onChange={(e) => {setPassword(e.target.value); setError("");}}/>
            </div>
            <button type="submit">Register</button>
            {error && <div className="error">{error}</div>}
        </form>
    </div>
    );
}

export default Register