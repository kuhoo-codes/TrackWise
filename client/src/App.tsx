import ItemList from "./components/ItemList";

const App = () => (
  <div className="min-h-screen bg-white flex flex-col items-center">
    {/* Main Content */}
    <main className="container flex-grow">
      <div className="text-center mb-16">
        <h1 className="text-4xl font-light tracking-tight text-gray-900 sm:text-5xl">
          TrackWise
        </h1>
      </div>
      <ItemList />
    </main>
  </div>
);

export default App;
