import { toast, Toaster, ToastBar } from "react-hot-toast";
import { BrowserRouter } from "react-router-dom";
import { AppRouter } from "./app/router/appRouter";

import "./App.css";

const App = () => (
  <BrowserRouter>
    <div className="App">
      <AppRouter />
      <Toaster reverseOrder>
        {(t) => (
          <div
            className="w-auto cursor-pointer"
            onClick={() => toast.dismiss(t.id)}
          >
            <ToastBar toast={t} />
          </div>
        )}
      </Toaster>
    </div>
  </BrowserRouter>
);

export default App;
