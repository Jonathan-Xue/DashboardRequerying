import React from 'react';
import './ReviewCard.scss'

export const ReviewCard = props => {
    return (
        <div className="review-card">
            <h2>{props.title}</h2>
            <p>Date Added: {props.date_added}</p>
            <p>Date Updated: {props.date_updated}</p>
            <p>Recommend: {props.recommend ? 'Yes' : 'No'}</p>
            <hr/>
            <p>{props.text}</p>
            <hr/>
            <div className="footer">
                <p>Num Helpful: {props.num_helpful}</p>
                <button style={{margin: 0}} onClick={() => {props.upvote(props.id)}}>Helpful</button>
            </div>


        </div>
    )
}