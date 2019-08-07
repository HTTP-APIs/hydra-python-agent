import React from 'react';
import AppBar from '@material-ui/core/AppBar'
import Toolbar from '@material-ui/core/Toolbar'
import Typography from '@material-ui/core/Typography'
import logo from '../../assets/images/hydra_eco_logo.png';
import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles(theme => ({
    hydraEcoLogo: {
      maxWidth: '30px',
      cursor: 'pointer'
    },
  }));

const NavBar = (props) => {
    const classes = useStyles();

    const toolbar = {
        AppBar: {
            backgroundColor: props.backgroundColor,
        },
        Typography: {
            fontSize: props.fontSize,
            flexGrow: 1,
        }
    };

    return (
        <div>
            <AppBar position="static" style={toolbar.AppBar} color={props.color}>
                <Toolbar>
                    <Typography variant="title" style={toolbar.Typography} color={props.fontColor}>
                        {props.text}
                    </Typography>
                    {props.onClick && (
                    <img src={logo} onClick={props.onClick}  className={classes.hydraEcoLogo} alt="logo" />
                    )}
                </Toolbar>
            </AppBar>
        </div>
    )
}

export default NavBar;