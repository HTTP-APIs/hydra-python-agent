import React from 'react';
import logo from '../assets/images/logo.svg';
import NavBar from '../components/navbar/NavBar'
import './app.scss';


export default function App() {
  return (
    <div>
      <NavBar text="rs" backgroundColor='primary' color='red'></NavBar>
      <header className="app-header">
        
        <img src={logo} className="app-logo" alt="logo" />
        <p>
          Edit <code>src/components/app/app.js</code> and save to reload.
        </p>
        <a
          className="app-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
      </header>
    </div>
  );
}
