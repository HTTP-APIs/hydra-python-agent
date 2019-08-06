import { createMuiTheme } from '@material-ui/core/styles';
import { purple } from '@material-ui/core/colors';

export default createMuiTheme({
    palette: {
        primary: {
          main: '#212121',
          dark: '#404040',
          light: '#eeeeee',
        },
        secondary: {
          main: '#757575',
          dark: '#000000',
          light: '#000000',
          contrastText: '#fff',
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

        }
    },
});