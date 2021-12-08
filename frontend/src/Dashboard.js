import React from 'react';
import './Dashboard.scss';

import { BarChart } from './BarChart';
import { getTopRatedProducts, getTopRecommendedProducts, getTopRatedManufacturers, getMostActiveUsers } from './actions';

class Dashboard extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            products: {},
            manufacturers: {},

            topRatedProducts: {},
            topRecommendedProducts: {},
            topRatedManufacturers: {},
            mostActiveUsers: {}
        };
    }

    componentDidMount() {
        this.updateData()
    }

    // Event Handlers
    updateData = () => {
        this.updateTopRatedProducts();
        this.updateTopRecommendedProducts();
        this.updateTopRatedManufacturers();
        this.updateMostActiveUsers()
    }

    // Update
    updateTopRatedProducts = (e) => {
        getTopRatedProducts().then(output => {
            let labels = [];
            let data = [];
            let backgroundColors = []
            output['data'].forEach(element => {
                labels.push(element['product_name']);
                data.push(element['avg_rating']);
                backgroundColors.push("hsl(" + 360 * Math.random() + ',' + (25 + 70 * Math.random()) + '%,' + (85 + 10 * Math.random()) + '%)');
            });

            this.setState({ 
                topRatedProducts: {
                    labels: labels,
                    datasets: [{
                        label: 'avg_rating',
                        data: data,
                        backgroundColor: backgroundColors,
                        borderWidth: 1,
                    }]
                } 
            });
        });
    }

    updateTopRecommendedProducts = (e) => {
        getTopRecommendedProducts().then(output => {
            let labels = [];
            let data = [];
            let backgroundColors = []
            output['data'].forEach(element => {
                labels.push(element['product_name']);
                data.push(element['num_recommended']);
                backgroundColors.push("hsl(" + 360 * Math.random() + ',' + (25 + 70 * Math.random()) + '%,' + (85 + 10 * Math.random()) + '%)');
            });

            this.setState({ 
                topRecommendedProducts: {
                    labels: labels,
                    datasets: [{
                        label: 'num_recommended',
                        data: data,
                        backgroundColor: backgroundColors,
                        borderWidth: 1,
                    }]
                } 
            });
        });
    }

    updateTopRatedManufacturers = (e) => {
        getTopRatedManufacturers().then(output => {
            let labels = [];
            let data = [];
            let backgroundColors = []
            output['data'].forEach(element => {
                labels.push(element['manufacturer_name']);
                data.push(element['avg_rating']);
                backgroundColors.push("hsl(" + 360 * Math.random() + ',' + (25 + 70 * Math.random()) + '%,' + (85 + 10 * Math.random()) + '%)');
            });

            this.setState({ 
                topRatedManufacturers: {
                    labels: labels,
                    datasets: [{
                        label: 'avg_rating',
                        data: data,
                        backgroundColor: backgroundColors,
                        borderWidth: 1,
                    }]
                } 
            });
        })
    }

    updateMostActiveUsers = (e) => {
        getMostActiveUsers().then(output => {
            let labels = [];
            let data = [];
            let backgroundColors = []
            output['data'].forEach(element => {
                labels.push(element['username']);
                data.push(element['num_reviews']);
                backgroundColors.push("hsl(" + 360 * Math.random() + ',' + (25 + 70 * Math.random()) + '%,' + (85 + 10 * Math.random()) + '%)');
            });

            this.setState({ 
                mostActiveUsers: {
                    labels: labels,
                    datasets: [{
                        label: 'num_reviews',
                        data: data,
                        backgroundColor: backgroundColors,
                        borderWidth: 1,
                    }]
                } 
            });
        })
    }

    render() {
        return (
            <div className="dashboard">
                <button className="refresh-button" onClick={this.updateData}>Refresh Data</button>
                <div className="chart-wrapper">
                    <BarChart data={this.state.topRatedProducts} title="Top Rated Products"/>
                </div>
                <div className="chart-wrapper">
                    <BarChart data={this.state.topRecommendedProducts} title="Top Recommended Products"/>
                </div>
                <div className="chart-wrapper">
                    <BarChart data={this.state.topRatedManufacturers} title="Top Rated Manufacturers"/>
                </div>
                <div className="chart-wrapper">
                    <BarChart data={this.state.mostActiveUsers} title="Most Active Users"/>
                </div>
            </div>
        )
    }
}

export default Dashboard;