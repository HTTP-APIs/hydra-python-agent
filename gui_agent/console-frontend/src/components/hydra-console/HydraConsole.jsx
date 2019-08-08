import React from 'react'
import Button from '@material-ui/core/Button';
import Grid from '@material-ui/core/Grid';

class HydraConsole extends React.Component {
    constructor(props) {
        super(props);
        this.classes = {
            button: {
              margin: '2px',
            },
            input: {
              display: 'none',
            },
            outContainer: {
                height: '40vh',
                backgroundColor: '#000',
            }
        }
    }

   render() {
       
        return (
            <Grid container className={this.classes.outContainer} style={this.classes.outContainer}>
                <Grid item xs={4} container
                    direction="column"
                    justify="space-between"
                    alignItems="center"> 
                    <Button variant="contained" color="secondary" className={this.classes.button} >
                        Drone Collection
                    </Button>
                    <Button variant="contained" className={this.classes.button}>
                        State Collection
                    </Button>
                    <Button variant="contained" className={this.classes.button}>
                        State Collection
                    </Button>
                    
                </Grid>
                <Grid item xs={4}> 
                    <Button variant="contained" color="secondary" className={this.classes.button} >
                        Drone Collection
                    </Button>
                    <Button variant="contained" className={this.classes.button}>
                        State Collection
                    </Button>
                    <Button variant="contained" className={this.classes.button}>
                        State Collection
                    </Button>
                </Grid>
                <Grid item xs={4}> 
                    <Button variant="contained" color="secondary" className={this.classes.button} >
                        Drone Collection
                    </Button>
                    <Button variant="contained" className={this.classes.button}>
                        State Collection
                    </Button>
                    <Button variant="contained" className={this.classes.button}>
                        State Collection
                    </Button>
                </Grid>
                <Grid item xs={12}>
                    <Button variant="contained" color="secondary" href="#contained-buttons" className={this.classes.button}>
                        Send Request
                    </Button>
                </Grid>
                <Grid item xs={12}
                      container
                      direction="column"
                      justify="center"
                      alignItems="center">
                    <span className={classes.outputContainerHeader} > Output</span>
                    <div className={classes.outputContainer}>
                    <Scrollbars>
                        {outputText}
                    </Scrollbars> 
                    </div>
                </Grid>
            </Grid>
        )
    }
}

export default withStyles(styles)(HydraConsole);