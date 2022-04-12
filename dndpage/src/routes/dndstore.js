// import './App.css';
import React, {
    // useState
    // useEffect
} from 'react';
import '../App.css';
// import {
//     UserCard
// } from './componets/userCard.jsx';
import useFetch from '../Hooks/useFetch.js'
import {
    Spinner
} from 'react-bootstrap';
import Table from 'react-bootstrap/Table'

function DNDStore() {
    // const [searchBy, setSearchBy] = useState(0)
    let {
        data,
        loading
    } = useFetch("http://127.0.0.1:5000/dndstore");
  return (
    <div>
          {loading ? 
            <div variant="primary" disabled>
              <Spinner
                as="span"
                animation="grow"
                size="sm"
                role="status"
                aria-hidden="true"
              />
              Loading...
            </div>:
            <div>
              <Table striped bordered hover>
                <thead>
                    <tr>
                    <th>#</th>
                    <th>Items</th>
                    <th>Cost</th>
                    <th>Currency</th>
                    </tr>
                </thead>
                <tbody>
                  {data.store.map((a, i) => {return (<tr><td>{i}</td><td>{a.item}</td><td>{a.cost}</td><td>{a.currency}</td></tr>)})}
                </tbody>
                </Table>
            </div>
          }
        </div>
  );
}

export default DNDStore;
