import React from 'react';
import logo from '../assets/images/logo.svg';
import NavBar from '../components/navbar/NavBar'
import HydraConsole from '../components/hydra-console/HydraConsole'
import HydraGraph from '../components/hydra-graph/HydraGraph'
import Grid from '@material-ui/core/Grid';
import './app.scss';


export default function App() {
  return (
    <div>
      <NavBar text="rs" backgroundColor='primary' color='primary'></NavBar>
      <Grid container>
      <Grid item xs={6}> 
          <HydraGraph></HydraGraph>
      </Grid>

      <Grid item xs={6}> 
        <HydraConsole></HydraConsole>
      </Grid>

      </Grid>
    </div>
  );
}
