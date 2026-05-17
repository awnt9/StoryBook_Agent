import { RouterProvider } from 'react-router-dom'
import router from './router/index'
import { Toaster } from 'sonner'

const App = () => {
  return (
    <>
      <RouterProvider router={router} />
      <Toaster 
        position="top-right"
        expand={true}
        richColors
        closeButton
      />
    </>
  )
}

export default App
