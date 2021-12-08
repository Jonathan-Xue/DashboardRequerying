import React from 'react';
import { Bar } from 'react-chartjs-2'

export const BarChart = props => {
    return (
        <Bar
            data={props.data}
            options={{
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: props.title,
                    },
                    legend: {
                        display: false,
                    }
                },
                responsive: true,
                scales: {
                    x: {
                        ticks: {
                            display: false
                        }
                    }
                }
            }}
        />
    )
}