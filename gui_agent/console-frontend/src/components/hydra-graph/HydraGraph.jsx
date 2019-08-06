import React from 'react'
import logo from '../../assets/images/logo.svg';
import GuiTheme from '../../app/gui-theme'

class HydraGraph extends React.Component {
   render() {
       return (
            <header className="app-header">
                
            <img src={logo} className="app-logo" alt="logo" />
            <p style={{color: GuiTheme.palette.text.secondary}} >
                This is the connected Hydra API
            </p>
            <a
            className="app-link"
            href="http://www.hydraecosystem.org/"
            target="_blank"
            rel="noopener noreferrer"
            >
            Learn about Hydra
            </a>
        </header>
       )
    }
}

export default HydraGraph;