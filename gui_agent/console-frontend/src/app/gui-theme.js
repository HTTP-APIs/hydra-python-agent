import { createMuiTheme } from '@material-ui/core/styles';
import { purple } from '@material-ui/core/colors';

export default createMuiTheme({
    palette: {
        primary: {
          main: '#212121',
          dark: '#404040',
          light: '#eeeeee',
          contrastText: '#fff',
        },
        secondary: {
          main: '#FBD20B',
          dark: '#c3a100',
          light: '#ffff54',
          contrastText: '#000',
        },
        contrastThreshold: 3,
        tonalOffset: 0.2,
        companyBlue: '#FF0000',
        companyRed: { 
            backgroundColor: '#E44D69',
            color: '#000',
        },
        accent: { 
            backgroundColor: purple[500], 
            color: '#000',
        },
        text: {
            primary: '#000000',
            secondary: '#585858',
        },
    },
});