import React, {useState, useEffect} from 'react';
import axios from 'axios';
import "./chat.css";
import {useNavigate} from 'react-router-dom';
import NewChatWindow from "../NewChatWindow/NewChatWindow"
import config from '../config/config.json';
import {IoSend} from "react-icons/io5";
import {hourglass} from 'ldrs';


interface Session {
    id: number;
    name: string;
    model: string;
    // include other properties here that a session might have
}

interface Message {
    role: string;
    content: string;
    isDone: boolean;
}

function Chat() {
    const navigate = useNavigate();
    const authToken = localStorage.getItem('authToken');
    const [sessions, setSessions] = useState<Session[]>([]);
    const [models, setModels] = useState<string[]>([]);
    const [selectedModel, setSelectedModel] = useState("gemma:7b");
    const [messages, setMessages] = useState<Message[]>([]);
    const [newMessage, setNewMessage] = useState('');
    const [currentSession, setNewSession] = useState<Session>();
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedSession, setSelectedSession] = useState<Number>(-1);

    const closeModal = () => {
        setIsModalOpen(false); // Function to close the modal
    };

    useEffect(() => {
        if (!authToken) {
            navigate('/login');
        } else {
            // Fetch sessions and models when the component mounts
            axios.get(`${config.backend_url}/session`, {headers: {Authorization: `Bearer ${authToken}`}})
                .then(response => {
                    const filteredSessions = response.data.list.map((session: any) => ({
                        id: session[0],
                        model: session[2],
                        name: session[3],
                    }));
                    setSessions(filteredSessions);
                })
                .catch(error => console.error(error));

            axios.get(`${config.backend_url}/models`)
                .then(response => {
                    setModels(response.data.models)
                })
                .catch(error => console.error(error));
        }
    }, [authToken, navigate]);

    const handleNewChat = () => {
        setIsModalOpen(true); // Set isModalOpen to true when the button is clicked
    };

    const handleNewSession = (model_name: string, title: string) => {
        // Function to handle the new session
        setMessages([]);
        setSelectedModel(model_name);
        let latest_session = sessions[sessions.length - 1].id + 1;
        let new_session: Session = {
            id: latest_session,
            name: title,
            model: model_name,
        }
        setSessions(sessions.concat(new_session));
        // Add the new session to the session list and display the selected model next to the chat
    };

    const handleSendMessage = () => {
        if (newMessage === "") {
            return;
        }
        let all_messages = messages;
        let user_message: Message = {
            role: "user",
            content: newMessage,
            isDone: true
        };
        let assitent_message: Message = {
            role: "assistant",
            content: "Message send",
            isDone: false
        };
        all_messages = all_messages.concat(user_message);
        all_messages = all_messages.concat(assitent_message);
        setMessages(all_messages);
        setNewMessage("");
        // Implement the functionality to send a message
    };

    const handleSessionSelection = async (session: Session) => {
        // Set the selected model to the model linked to the session
        setSelectedModel(session.model);

        // Fetch the messages for the selected session
        const response = await axios.get(`${config.backend_url}/history/${session.id}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (response.status === 200) {
            // Set the messages state to the fetched messages
            setMessages(response.data.messages);
        }
    };
    hourglass.register();
    return (
        <div className="MainFrame">
            <div className="SelectionPanel">
                <div className="SectionInSelection">
                    <button className="NewChatButton" onClick={handleNewChat}>New Chat</button>
                </div>
                <div className="SectionInSelection">
                    <button className="PluginButton">Plugin</button>
                </div>
                <div className="ScrolableSessionPannel">
                    {sessions.map(session => (
                        <div className="SessionSelection">
                            <button className="SessionSelectionButton"
                                    onClick={() => handleSessionSelection(session)}>{session.name}</button>

                        </div>

                    ))}

                </div>

            </div>
            <div className="ChatContainer">
                <div className="ChatFrame">
                    {messages.map((message) => (
                        <div className="ChatLine">
                            {message.role === "assistant" ? (
                                <>
                                    <div className="AssistantChatMessage">
                                        <h3>Assitant</h3>
                                        <p>{message.content}</p>
                                    </div>
                                    <div>
                                        {message.isDone ? <></> : <l-hourglass
                                            size="40"
                                            bg-opacity="0.1"
                                            speed="1.75"
                                            color="purple"
                                        ></l-hourglass>}
                                    </div>
                                    <div className="UserChatMessagePlaceHolder"></div>
                                </>
                            ) : (
                                <>
                                    <div className="AssistantChatMessagePlaceHolder"></div>
                                    <div className="UserChatMessage">
                                        <h3>User</h3>
                                        <p>{message.content}</p>
                                    </div>
                                </>
                            )}
                        </div>
                    ))}
                </div>
                <div className="ChatInput">
                    <select value={selectedModel} onChange={e => setSelectedModel(e.target.value)}>
                        {models.map(model => (
                            <option key={model} value={model}>{model}</option>
                        ))}
                    </select>
                    <div className="InputButtonWrapper">
                        <textarea value={newMessage} onChange={e => setNewMessage(e.target.value)}/>
                        <button onClick={handleSendMessage}>
                            <IoSend style={{color: "8000ff"}}/>
                        </button>
                    </div>
                </div>
            </div>
            <NewChatWindow models={models} onNewSession={handleNewSession} isOpen={isModalOpen} onClose={closeModal}/>
        </div>

    );
}

export default Chat;