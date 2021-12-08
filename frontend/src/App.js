import React from 'react';
import {
	BrowserRouter,
    Link,
	Route,
	Switch
} from "react-router-dom";
import {
    Container,
    Nav,
    Navbar
} from 'react-bootstrap';
import './App.scss';

import CRUD from './CRUD'
import Dashboard from './Dashboard';
import Reviews from './Reviews';

export default function App() {
	return (
		<BrowserRouter>
            <Navbar bg="dark" variant="dark">
                <Container>
                <Navbar.Brand as={Link} to="/">NullDB</Navbar.Brand>
                <Nav className="me-auto">
                    <Nav.Link as={Link} to="/dashboard">Dashboard</Nav.Link>
                    <Nav.Link as={Link} to="/reviews">Reviews</Nav.Link>
                    <Nav.Link as={Link} to="/crud">CRUD</Nav.Link>
                </Nav>
                </Container>
            </Navbar>
			<Switch>
				<Route path="/dashboard">
					<Dashboard />
				</Route>
                <Route path="/reviews">
                    <Reviews />
                </Route>
				<Route path="/crud">
                    <CRUD />
				</Route>
				<Route path="/"></Route>
			</Switch>
		</BrowserRouter>
	);
};
