import React from 'react';
import './index.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import {
    BrowserRouter,
    Routes,
    Route,
  } from "react-router-dom";

import { render } from "react-dom";
import App from "./App";
import DNDStore from "./routes/dndstore";


const rootElement = document.getElementById("root");
render(<BrowserRouter>
    <Routes>
      <Route path="/" element={<App />} />
      <Route path="dndstore" element={<DNDStore />} />
    </Routes>
  </BrowserRouter>, rootElement);