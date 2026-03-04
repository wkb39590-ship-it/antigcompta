import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import './index.css'

console.log('[Main] Rendering root...')
try {
    const root = document.getElementById('root')
    if (!root) throw new Error('Root element not found')
    ReactDOM.createRoot(root).render(
        <React.StrictMode>
            <BrowserRouter>
                <App />
            </BrowserRouter>
        </React.StrictMode>,
    )
    console.log('[Main] Render called successfully')
} catch (e) {
    console.error('[Main] Critical error during mount:', e)
}
