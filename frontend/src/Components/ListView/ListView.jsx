import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

import Button from '@mui/material/Button';

const ListView = () => {
  const [count, setCount] = useState(0)

  return (
    <>
      <h1 className="text-3xl text-blue-500 underline">
      Hello world!
    </h1>
    <Button variant="contained">Hello world</Button>
    </>
  )
}

export default ListView
