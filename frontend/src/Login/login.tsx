import React from "react";
import "./login.css";
import { FaUserAlt } from "react-icons/fa";
import { FaLock } from "react-icons/fa";
function Login(){
    return (
    <div className="wrapper">
        <form action="">
            <h1>Login</h1>
            <div className="input-box">
                <FaUserAlt className="icon"/>
                <input type="text" placeholder="Username" required maxLength={64}/>
            </div>
            <div className="input-box">
                <FaLock className="icon"/>
                <input type="password" placeholder="Password" required/>
            </div>
            <button type="submit">Login</button>
            <div className="register-link">
                <p><a href="#"> Click here to register</a></p>
            </div>
        </form>

    </div>
    );
}

export default Login