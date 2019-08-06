import React from 'react';
import AppBar from '@material-ui/core/AppBar'
import Toolbar from '@material-ui/core/Toolbar'
import Typography from '@material-ui/core/Typography'

const NavBar = (props) => {
    const toolbar = {
        AppBar: {
            backgroundColor: props.backgroundColor,
        },
        Typography: {
            fontSize: props.fontSize,
        }
    };

    return (
        <div>
            <AppBar position="static" style={toolbar.AppBar} color={props.color}>
                <Toolbar>
                    <Typography variant="title" style={toolbar.Typography} color={props.fontColor}>
                        {props.text}
                    </Typography>
                </Toolbar>
            </AppBar>
        </div>
    )
}

export default NavBar;