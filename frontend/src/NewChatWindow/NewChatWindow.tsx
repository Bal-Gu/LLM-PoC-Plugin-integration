import React, { useState } from 'react';
import axios from 'axios';

interface NewChatWindowProps {
    models: string[];
    onNewSession: (data: any) => void;
    isOpen: boolean;
    onClose: () => void;
}
const NewChatWindow: React.FC<NewChatWindowProps> = ({ models, onNewSession, isOpen, onClose }) => {
    const [model, setModel] = useState(models[0]);
    const [sessionName, setSessionName] = useState('');

    const handleSubmit = async (event: { preventDefault: () => void; }) => {
        event.preventDefault();

        const response = await axios.post('/newsession', {
            model_name: model,
            session_name: sessionName
        }, {
            headers: {
                'Authorization': 'Bearer your-authorization-key'
            }
        });

        if (response.status === 200) {
            onNewSession(response.data);
            onClose();
        }
    };

    if (!isOpen) {
        return null;
    }

    return (
        <div className="MainFrame">
            <form onSubmit={handleSubmit}>
                <select value={model} onChange={e => setModel(e.target.value)}>
                    {models.map(model => (
                        <option key={model} value={model}>{model}</option>
                    ))}
                </select>
                <input
                    type="text"
                    value={sessionName}
                    onChange={e => setSessionName(e.target.value)}
                    placeholder="Session name"
                />
                <button type="submit" className="NewChatButton">Create Session</button>
            </form>
        </div>
    );
};

export default NewChatWindow;