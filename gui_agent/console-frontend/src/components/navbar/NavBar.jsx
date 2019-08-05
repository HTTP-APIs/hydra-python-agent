import React from 'react';
import AppBar from '@material-ui/core/AppBar'
import Toolbar from '@material-ui/core/Toolbar'
import Typography from '@material-ui/core/Typography'
import { pink } from '@material-ui/core/colors';

const NavBar = (props) => {
    const toolbar = {
        background : props.backgroundColor ? props.backgroundColor : 'primary',
    };
    
    const toolbarTitle = {
        color: props.color ? props.color : 'primary',
    };

    return (
        <div>
            <AppBar position="static" style={toolbar}>
                <Toolbar color="black">
                    <Typography variant="title" style={toolbarTitle}>
                        Hydra Agent GUI {props.text}
                    </Typography>
                </Toolbar>
            </AppBar>
        </div>
    )
}

export default NavBar;