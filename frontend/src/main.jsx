import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'
import FirstPage from './first_page.jsx'
import SecondPage from './second_page.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<FirstPage/>}/>
        <Route path="single-piece/:sessionId" element={<SecondPage/>}/>
      </Routes>
    </BrowserRouter>
  </StrictMode>,
)
