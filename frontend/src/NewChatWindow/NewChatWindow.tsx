import React, {useEffect, useState} from 'react';
import axios from 'axios';
import "./NewChatWindow.css"
import "../Login/login.css"
import config from '../config/config.json';
import {Session} from "inspector";

interface NewChatWindowProps {
    models: string[];
    onNewSession: (model_name: string, title: string, index: number) => void;
    isOpen: boolean;
    onClose: () => void;
}

const NewChatWindow: React.FC<NewChatWindowProps> = ({models, onNewSession, isOpen, onClose}) => {
    const [model, setModel] = useState<string>(models[0]);
    const [sessionName, setSessionName] = useState('');
    const authToken = localStorage.getItem('authToken') || "";

    // Fetch model data when component mounts
    useEffect(() => {
        if (models.length > 0) {
            setModel(models[0]);
        }
    }, [models]);

    const handleSubmit = async (event: { preventDefault: () => void; }) => {
        event.preventDefault();
        if (model == null) {
            setModel(models[0]);
        }
        const response = await axios.post(`${config.backend_url}/newsession`, {
            model_name: model,
            session_name: sessionName
        }, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (response.status === 200) {
            onNewSession(model, sessionName, response.data["session_id"]);
            onClose();
        }
    };

    if (!isOpen) {
        return null;
    }

    return (
        <div className="NewChatModal">
            <form onSubmit={handleSubmit}>
                <div className="ModalAllignment">
                    <h1>Model selection</h1>
                    <select value={model} onChange={e => setModel(e.target.value)}>
                        {models.map(model => (
                            <option key={model} value={model}>{model}</option>
                        ))}
                    </select>
                </div>
                <div className="ModalAllignment">
                    <h1>Session name</h1>
                    <input
                        type="text"
                        value={sessionName}
                        onChange={e => setSessionName(e.target.value)}
                        placeholder="Give your  session a title"
                    />
                </div>
                <div className="ModalAllignment">
                    <button type="submit" className="button">Create Session</button>
                </div>
            </form>
        </div>
    );
};

export default NewChatWindow;