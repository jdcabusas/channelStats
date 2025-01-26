import { useState } from 'react'

import dayjs, { Dayjs } from 'dayjs';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';


const Search = () => {
    const [toValue, setToValue] = useState(dayjs(''));
    const [fromValue, setFromValue] = useState(dayjs(''));
    const [fromFormattedDate, setFromFormattedDate] = useState('');
    const [toFormattedDate, setToFormattedDate] = useState('');

    const setDate = (newValue, flag) => {
        const date = new Date(newValue?.$d);
        const formattedDate = date.toISOString().split('T')[0];

        if(flag === 'F') {
            setFromValue(newValue)
            setFromFormattedDate(formattedDate);
        } else {
            setToValue(newValue)
            setToFormattedDate(formattedDate);
        }
    }


  return (
    <>      
    <div>
    <LocalizationProvider dateAdapter={AdapterDayjs}>
        <DatePicker value={toValue} label="To" defaultValue={dayjs('')} onChange={(toValue) => setDate(toValue, 'T')}/>
        <DatePicker
          label="From"
          value={fromValue}
          onChange={(fromValue) => setDate(fromValue, 'F')}
        /> 
    </LocalizationProvider>
    </div>
    
    </>
  )
}

export default Search
