import { BrowserRouter } from "react-router-dom";
import { AppRouter } from "./app/router/appRouter";
import "./App.css";

const App = () => (
  <BrowserRouter>
    <div className="App">
      <AppRouter />
    </div>
  </BrowserRouter>
);

export default App;
