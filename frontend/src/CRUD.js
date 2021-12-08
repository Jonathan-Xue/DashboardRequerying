import React from 'react';
import './CRUD.scss';

import { resetDB, autoinsertReviews } from './actions';

class CRUD extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            currProductID: -1,
            products: [],
        };
    }

    // Event Handlers
    resetDatabase = (e) => {
        resetDB().then(data => {
           alert('Done! Database reset.')
        });
    }

    ingestData = numReviews => e => {
        autoinsertReviews(numReviews).then(data => {
            alert('Done! ' + numReviews + ' reviews inserted.');
        });
    }

    render() {
        return (
            <div className="crud">
                <button className="reset" onClick={this.resetDatabase}>Reset Database</button>

                <div className="crud-table">
                    <div className="row">
                        <button className="ingest" onClick={this.ingestData(1)}>Ingest 1 Entry</button>
                        <button className="ingest" onClick={this.ingestData(10)}>Ingest 10 Entries</button>
                    </div>
                    <div className="row">
                        <button className="ingest" onClick={this.ingestData(100)}>Ingest 100 Entries</button>
                        <button className="ingest" onClick={this.ingestData(1000)}>Ingest 1000 Entries</button>
                    </div>
                    <div className="row">
                        <button className="ingest" onClick={this.ingestData(10000)}>Ingest 10000 Entries</button>
                        <button className="ingest" onClick={this.ingestData(100000)}>Ingest 100000 Entries</button>
                    </div>
                </div>
            </div>
        )
    }
}

export default CRUD