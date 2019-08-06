import React from 'react';
import NavBar from '../components/navbar/NavBar'
import HydraConsole from '../components/hydra-console/HydraConsole'
import HydraGraph from '../components/hydra-graph/HydraGraph'
import Grid from '@material-ui/core/Grid';
import './app.scss';
import GuiTheme from './gui-theme'
import { ThemeProvider } from '@material-ui/styles';


export default function App() {
  return (
    <ThemeProvider theme={GuiTheme}>
      <NavBar text="Hydra Agent GUI" fontSize='1.5em' backgroundColor={GuiTheme.palette.primary.main} color='primary'></NavBar>
      <Grid container>
        <Grid item xs={6} > 
          <NavBar text="Hydra API" fontSize='1.3em'
            backgroundColor={GuiTheme.palette.primary.light}
            fontColor="textSecondary"></NavBar>
          <HydraGraph></HydraGraph>
        </Grid>

        <Grid item xs={6} color='primary'>
          <NavBar text="Agent Console" fontSize='1.3em'
            backgroundColor={GuiTheme.palette.primary.dark}
          ></NavBar> 
          <HydraConsole  color='primary' ></HydraConsole>
        </Grid>
      </Grid>
    </ThemeProvider>
  );
}
