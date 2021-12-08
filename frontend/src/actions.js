import { config } from './config'

// Reset
export const resetDB = () => new Promise((resolve, reject) => {
    let url = config.API_ENDPOINT + '/reset';

    fetch(url, {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({}),
        mode: 'cors',
    }).then(response => response.json()).then(data => {
        resolve(data);
    });
});

// Post
export const autoinsertReviews = (count = 1) => new Promise((resolve, reject) => {
    let url = config.API_ENDPOINT + '/autoinsert?' + new URLSearchParams({
        count: count
    });

    fetch(url, {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({}),
        mode: 'cors',
    }).then(response => response.json()).then(data => {
        resolve(data);
    });
});

export const insertReview = (title, text, rating, num_helpful, recommend, user_id, product_id) => new Promise((resolve, reject) => {
    let url = config.API_ENDPOINT + '/insert-review';
    let curr_date = new Date().toISOString().replace(/T/, ' ').replace(/\..+/, '');

    fetch(url, {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({   
            title: title,
            text: text,
            rating: rating,
            num_helpful: num_helpful,
            recommend: recommend,
            date_added: curr_date,
            date_updated: curr_date,
            user_id: user_id,
            product_id: product_id
        }),
        mode: 'cors',
    }).then(response => response.json()).then(data => {
        resolve(data);
    });
});

export const updateReview = (id, title, text, rating, recommend) => new Promise((resolve, reject) => {
    let url = config.API_ENDPOINT + '/update-review';

    fetch(url, {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            id: id,
            title: title,
            text: text,
            rating: rating,
            recommend: recommend,
            date_updated: new Date().toISOString().replace(/T/, ' ').replace(/\..+/, '')
        }),
        mode: 'cors',
    }).then(response => response.json()).then(data => {
        resolve(data);
    });
});

export const upvoteReview = (id) => new Promise((resolve, reject) => {
    let url = config.API_ENDPOINT + '/upvote-review';

    fetch(url, {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            id: id
        }),
        mode: 'cors',
    }).then(response => response.json()).then(data => {
        resolve(data);
    });
});

// GET
export const getUsers = () => new Promise((resolve, reject) => {
    let url = config.API_ENDPOINT + '/users?';

    fetch(url, {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        mode: 'cors',
    }).then(response => response.json()).then(data => {
        resolve(data);
    });
});

export const getProducts = () => new Promise((resolve, reject) => {
    let url = config.API_ENDPOINT + '/products?';

    fetch(url, {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        mode: 'cors',
    }).then(response => response.json()).then(data => {
        resolve(data);
    });
});

export const getProductCategories = () => new Promise((resolve, reject) => {
    let url = config.API_ENDPOINT + '/product-categories?';

    fetch(url, {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        mode: 'cors',
    }).then(response => response.json()).then(data => {
        resolve(data);
    });
});

export const getManufacturers = () => new Promise((resolve, reject) => {
    let url = config.API_ENDPOINT + '/manufacturers?';

    fetch(url, {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        mode: 'cors',
    }).then(response => response.json()).then(data => {
        resolve(data);
    });
});

// Aggregates
export const getTopRatedProducts = (count = 25) => new Promise((resolve, reject) => {
    let url = config.API_ENDPOINT + '/top-rated-products?' + new URLSearchParams({
        count: count
    });

    fetch(url, {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        mode: 'cors',
    }).then(response => response.json()).then(data => {
        resolve(data);
    });
});

export const getTopRecommendedProducts = (count = 10) => new Promise((resolve, reject) => {
    let url = config.API_ENDPOINT + '/top-recommended-products?' + new URLSearchParams({
        count: count
    });

    fetch(url, {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        mode: 'cors',
    }).then(response => response.json()).then(data => {
        resolve(data);
    });
});

export const getTopRatedManufacturers = (count = 5) => new Promise((resolve, reject) => {
    let url = config.API_ENDPOINT + '/top-rated-manufacturers?' + new URLSearchParams({
        count: count
    });

    fetch(url, {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        mode: 'cors',
    }).then(response => response.json()).then(data => {
        resolve(data);
    });
});

export const getMostActiveUsers = (count = 10) => new Promise((resolve, reject) => {
    let url = config.API_ENDPOINT + '/most-active-users?' + new URLSearchParams({
        count: count
    });

    fetch(url, {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        mode: 'cors',
    }).then(response => response.json()).then(data => {
        resolve(data);
    });
});

export const getMostHelpfulReviews = (product_id, count = 5) => new Promise((resolve, reject) => {
    let url = config.API_ENDPOINT + '/most-helpful-reviews?' + new URLSearchParams({
        product_id: product_id,
        count: count
    });

    fetch(url, {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        mode: 'cors',
    }).then(response => response.json()).then(data => {
        resolve(data);
    });
});

export const getMostRecentReviews = (product_id, count = 5) => new Promise((resolve, reject) => {
    let url = config.API_ENDPOINT + '/most-recent-reviews?' + new URLSearchParams({
        product_id: product_id,
        count: count
    });

    fetch(url, {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        mode: 'cors',
    }).then(response => response.json()).then(data => {
        resolve(data);
    });
});