import React from 'react';
import Select from 'react-select';
import './Reviews.scss';

import { ReviewCard } from './ReviewCard';
import { getProducts, getMostHelpfulReviews, getMostRecentReviews, upvoteReview } from './actions';

class Reviews extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            currProductID: -1,
            products: [],

            mostHelpfulReviews: [],
            mostRecentReviews: [],
        };
    }

    componentDidMount() {
        this.updateProducts();
    }

    // Event Handlers
    updateData = () => {
        this.updateProducts();
        this.updateMostHelpfulReviews();
        this.updateMostRecentReviews();
    }

    dropdownSelect = (option) => {
        this.setState({
            currProductID: option['value']
        }, () => {
            this.updateMostHelpfulReviews();
            this.updateMostRecentReviews();
        });
    }

    upvote = (review_id) => {
        upvoteReview(review_id).then(data => {
            this.updateData();
        });
    }

    // Update
    updateProducts = (e) => {
        getProducts().then(output => {
            let data = [];
            output['data'].forEach(element => {
                data.push({
                    value: element['product_id'],
                    label: element['product_name']
                });
            });
            
            this.setState({
                products: data
            });
        });
    }

    updateMostHelpfulReviews = (e) => {
        getMostHelpfulReviews(this.state.currProductID).then(output => {
            let data = output['data'];
            console.log(data);
            this.setState({
                mostHelpfulReviews: data
            })
        });
    }

    updateMostRecentReviews = (e) => {
        getMostRecentReviews(this.state.currProductID).then(output => {
            let data = output['data'];
            this.setState({
                mostRecentReviews: data
            })
        });
    }

    render() {
        return (
            <div className="reviews">
                <div className="reviews-header">
                    <button className="refresh-button" onClick={this.updateData}>&#8635;</button>
                    <Select 
                        className="select"
                        onChange={this.dropdownSelect}
                        options={this.state.products} 
                    />
                </div>

                <div className="reviews-container">
                    <div className="list">
                        <h3>Most Helpful Reviews</h3>
                        <div className="content">
                            {
                                this.state.mostHelpfulReviews.map((element) => 
                                    <ReviewCard 
                                        key={element['id']}
                                        id={element['id']}
                                        title={element['title']}
                                        date_added={element['date_added']}
                                        date_updated={element['date_updated']}
                                        text={element['text']}
                                        num_helpful={element['num_helpful']}
                                        recommend={element['recommend']}

                                        upvote={this.upvote}
                                    />
                                )
                            }
                        </div>
                    </div>
                    <div className="list">
                        <h3>Most Recent Reviews</h3>
                        <div className="content">
                            {
                                this.state.mostRecentReviews.map((element) => 
                                    <ReviewCard 
                                        key={element['id']}
                                        title={element['title']}
                                        date_added={element['date_added']}
                                        date_updated={element['date_updated']}
                                        text={element['text']}
                                        num_helpful={element['num_helpful']}
                                        recommend={element['recommend']}
                                    />
                                )
                            }
                        </div>
                    </div>
                </div>
            </div>
        )
    }
}

export default Reviews