import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import Search from "../src/Components/Search/Search"
import Video from "../src/Components/Video/Video"

import Button from '@mui/material/Button';
import { DatePicker } from 'antd';

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
    <Search/>
    <Video />
    </>
  )
}

export default App
