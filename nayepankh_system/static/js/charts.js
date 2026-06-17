document.addEventListener('DOMContentLoaded', () => {
    fetch('/api/chart-data')
        .then(response => response.json())
        .then(data => {
            // Beneficiaries per Program Chart (Bar Chart)
            const beneficiariesCtx = document.getElementById('beneficiariesChart').getContext('2d');
            new Chart(beneficiariesCtx, {
                type: 'bar',
                data: {
                    labels: data.beneficiariesPerProgram.labels,
                    datasets: [{
                        label: '# of Beneficiaries',
                        data: data.beneficiariesPerProgram.data,
                        backgroundColor: [
                            'rgba(255, 99, 132, 0.5)',
                            'rgba(54, 162, 235, 0.5)',
                            'rgba(255, 206, 86, 0.5)',
                            'rgba(75, 192, 192, 0.5)',
                            'rgba(153, 102, 255, 0.5)',
                            'rgba(255, 159, 64, 0.5)'
                        ],
                        borderColor: [
                            'rgba(255, 99, 132, 1)',
                            'rgba(54, 162, 235, 1)',
                            'rgba(255, 206, 86, 1)',
                            'rgba(75, 192, 192, 1)',
                            'rgba(153, 102, 255, 1)',
                            'rgba(255, 159, 64, 1)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });

            // Volunteers by City Chart (Doughnut Chart)
            const volunteersCtx = document.getElementById('volunteersChart').getContext('2d');
            new Chart(volunteersCtx, {
                type: 'doughnut',
                data: {
                    labels: data.volunteersByCity.labels,
                    datasets: [{
                        label: 'Volunteers',
                        data: data.volunteersByCity.data,
                        backgroundColor: [
                            '#FF6384',
                            '#36A2EB',
                            '#FFCE56',
                            '#4BC0C0',
                            '#9966FF',
                            '#FF9F40'
                        ],
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                }
            });
        })
        .catch(error => console.error('Error fetching chart data:', error));
});