import ItemList from './components/ItemList'

function App() {
  return (
    <div className="min-h-screen bg-white">
      {/* Navigation Bar */}
      <nav className="border-b border-gray-100">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <span className="text-xl font-light tracking-tight text-gray-900">TrackWise</span>
            </div>
            <div className="flex items-center space-x-8">
              <a href="#" className="text-sm text-gray-500 hover:text-gray-900 transition-colors duration-200">
                About
              </a>
              <a href="#" className="text-sm text-gray-500 hover:text-gray-900 transition-colors duration-200">
                Documentation
              </a>
              <a href="#" 
                 className="text-sm text-gray-900 border border-gray-200 px-4 py-2 rounded-full hover:bg-gray-50 transition-colors duration-200">
                GitHub
              </a>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-16">
          <h1 className="text-4xl font-light tracking-tight text-gray-900 sm:text-5xl">
            Item Management System
          </h1>
          <p className="mt-4 text-base text-gray-500 max-w-2xl mx-auto">
            A minimal and efficient way to track and manage your items. Simple, clean, and organized.
          </p>
        </div>

        {/* Item List Component */}
        <ItemList />
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-100 mt-24">
        <div className="max-w-5xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
          <div className="text-center text-sm text-gray-400">
            Designed and built with care
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
