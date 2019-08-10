import React from 'react'
import Button from '@material-ui/core/Button';
import { withStyles } from '@material-ui/styles';

const styles = theme => ({
    collectionButton: {
        width: '80%'
    },
    collectionSelectedButton: { 
        backgroundColor: '#f00',  
    }
});

class CollectionButtons extends React.Component {
    constructor(props) {
        super(props);
        var buttons = []
        Object.keys(this.props.collections).map( (collection) => {
            buttons[collection] = false
        })

        const selectedButton = Object.keys(this.props.collections)[0];
        buttons[ selectedButton ] = true

        this.state = {
            buttons: buttons,
            selectedButton: selectedButton,
        }
    }

    selectButton(clickedButton){
        var updatedButtons = this.state.buttons.slice();
        updatedButtons[this.state.selectButton] = false;
        updatedButtons[clickedButton] = true;

        this.setState({
            buttons: updatedButtons,
            selectButton: clickedButton
        })
         
    }

    generateButtons(){
        const collectionsArray = Object.keys(this.props.collections);
        
        const { classes } = this.props;

        var buttons = collectionsArray.map( (currProperty, index) => { 
            return(<Button
                key={currProperty}
                variant="contained"
                color={this.state.buttons[currProperty] ? "secondary" : null}
                className={classes.collectionButton}
                onClick={ (e) => {this.selectButton(currProperty); this.props.selectCollection(currProperty)}}>
                {this.props.collections[currProperty].collection.name}
            </Button>)})
        return buttons;
    }

    render() {
        
        return this.generateButtons()
    }
}

export default withStyles(styles)(CollectionButtons);
