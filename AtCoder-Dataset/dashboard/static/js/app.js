// --- Global Utilities ---

// Dark Mode Toggle
const themeToggle = document.getElementById('theme-toggle');
if (themeToggle) {
    const currentTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-bs-theme', currentTheme);
    
    themeToggle.addEventListener('click', () => {
        const newTheme = document.documentElement.getAttribute('data-bs-theme') === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-bs-theme', newTheme);
        localStorage.setItem('theme', newTheme);
    });
}

// Copy Code/URL buttons
document.querySelectorAll('.copy-code-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const targetId = this.parentElement.nextElementSibling.querySelector('code').id;
        const text = document.getElementById(targetId).innerText;
        navigator.clipboard.writeText(text).then(() => {
            const originalText = this.innerText;
            this.innerText = 'Copied!';
            setTimeout(() => { this.innerText = originalText; }, 2000);
        });
    });
});

const copyUrlBtn = document.getElementById('copyUrlBtn');
if (copyUrlBtn) {
    copyUrlBtn.addEventListener('click', function() {
        navigator.clipboard.writeText(window.location.href).then(() => {
            const originalHtml = this.innerHTML;
            this.innerHTML = '<i class="bi bi-check2"></i> Copied!';
            setTimeout(() => { this.innerHTML = originalHtml; }, 2000);
        });
    });
}

// --- Problems Page Logic ---
const problemsTableBody = document.getElementById('problemsTableBody');
if (problemsTableBody) {
    let state = {
        limit: 25,
        offset: 0,
        search: '',
        topic: '',
        difficulty: '',
        contest_id: '',
        sort_by: 'problem_id',
        sort_order: 'ASC'
    };

    const fetchProblems = async () => {
        const query = new URLSearchParams(state).toString();
        try {
            const response = await fetch(`/api/problems?${query}`);
            const data = await response.json();
            renderTable(data.data);
            renderPagination(data.total);
            document.getElementById('totalCountDisplay').innerText = `Showing ${data.data.length} of ${data.total} problems`;
        } catch (error) {
            console.error('Error fetching problems:', error);
        }
    };

    const renderTable = (problems) => {
        problemsTableBody.innerHTML = '';
        if (problems.length === 0) {
            problemsTableBody.innerHTML = '<tr><td colspan="8" class="text-center py-4">No problems found</td></tr>';
            return;
        }

        problems.forEach(p => {
            const tr = document.createElement('tr');
            tr.onclick = () => window.location.href = `/problem/${p.problem_id}`;
            
            const diffClass = p.difficulty ? p.difficulty.toLowerCase().replace(' ', '-') : '';
            const topicBadge = p.topic ? `<span class="badge bg-primary">${p.topic}</span>` : '<span class="text-muted">-</span>';
            const diffBadge = p.difficulty ? `<span class="badge difficulty-badge ${diffClass}">${p.difficulty}</span>` : '<span class="text-muted">-</span>';
            
            tr.innerHTML = `
                <td>${p.problem_id}</td>
                <td><span class="badge bg-secondary">${p.contest_id}</span></td>
                <td class="fw-bold">${p.title || 'N/A'}</td>
                <td>${topicBadge}</td>
                <td>${p.subtopic || '-'}</td>
                <td>${diffBadge}</td>
                <td>${p.rating !== null ? p.rating : '-'}</td>
                <td class="text-end">
                    <a href="/problem/${p.problem_id}" class="btn btn-sm btn-outline-primary" onclick="event.stopPropagation();">View</a>
                </td>
            `;
            problemsTableBody.appendChild(tr);
        });
    };

    const renderPagination = (total) => {
        const totalPages = Math.ceil(total / state.limit);
        const currentPage = Math.floor(state.offset / state.limit) + 1;
        const pagination = document.getElementById('paginationControls');
        pagination.innerHTML = '';

        if (totalPages <= 1) return;

        const addPageBtn = (page, text, disabled = false, active = false) => {
            const li = document.createElement('li');
            li.className = `page-item ${disabled ? 'disabled' : ''} ${active ? 'active' : ''}`;
            const a = document.createElement('a');
            a.className = 'page-link';
            a.href = '#';
            a.innerHTML = text;
            if (!disabled && !active) {
                a.onclick = (e) => {
                    e.preventDefault();
                    state.offset = (page - 1) * state.limit;
                    fetchProblems();
                };
            }
            li.appendChild(a);
            pagination.appendChild(li);
        };

        addPageBtn(currentPage - 1, 'Previous', currentPage === 1);
        
        let startPage = Math.max(1, currentPage - 2);
        let endPage = Math.min(totalPages, startPage + 4);
        if (endPage - startPage < 4) {
            startPage = Math.max(1, endPage - 4);
        }

        for (let i = startPage; i <= endPage; i++) {
            addPageBtn(i, i, false, i === currentPage);
        }

        addPageBtn(currentPage + 1, 'Next', currentPage === totalPages);
    };

    // Event Listeners for Filters
    let debounceTimer;
    document.getElementById('searchInput').addEventListener('input', (e) => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            state.search = e.target.value;
            state.offset = 0;
            fetchProblems();
        }, 300);
    });

    ['topicFilter', 'difficultyFilter', 'contestFilter', 'limitSelect'].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('change', (e) => {
                const key = id.replace('Filter', '').replace('Select', '');
                state[key] = e.target.value;
                if (key === 'limit') state.limit = parseInt(e.target.value);
                state.offset = 0;
                fetchProblems();
            });
        }
    });

    // Event Listeners for Sorting
    document.querySelectorAll('.sortable').forEach(th => {
        th.addEventListener('click', () => {
            const sortBy = th.getAttribute('data-sort');
            if (state.sort_by === sortBy) {
                state.sort_order = state.sort_order === 'ASC' ? 'DESC' : 'ASC';
            } else {
                state.sort_by = sortBy;
                state.sort_order = 'ASC';
            }
            
            document.querySelectorAll('.sortable').forEach(el => {
                el.classList.remove('sort-asc', 'sort-desc');
            });
            th.classList.add(state.sort_order === 'ASC' ? 'sort-asc' : 'sort-desc');
            
            state.offset = 0;
            fetchProblems();
        });
    });

    // Export CSV
    document.getElementById('exportCsvBtn').addEventListener('click', async () => {
        const exportState = { ...state, limit: 10000, offset: 0 }; // Export all matching
        const query = new URLSearchParams(exportState).toString();
        try {
            const response = await fetch(`/api/problems?${query}`);
            const data = await response.json();
            
            if (data.data.length === 0) return;
            
            const headers = ['Problem ID', 'Contest ID', 'Title', 'Topic', 'Subtopic', 'Difficulty', 'Rating'];
            let csvContent = "data:text/csv;charset=utf-8," + headers.join(',') + '\n';
            
            data.data.forEach(p => {
                const row = [
                    p.problem_id, 
                    p.contest_id, 
                    `"${(p.title || '').replace(/"/g, '""')}"`, 
                    `"${p.topic || ''}"`, 
                    `"${p.subtopic || ''}"`, 
                    p.difficulty, 
                    p.rating
                ];
                csvContent += row.join(',') + '\n';
            });
            
            const encodedUri = encodeURI(csvContent);
            const link = document.createElement('a');
            link.setAttribute('href', encodedUri);
            link.setAttribute('download', 'atcoder_problems.csv');
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } catch (error) {
            console.error('Export failed:', error);
        }
    });

    // Initial Load
    fetchProblems();
}

// --- Statistics Page Logic ---
if (document.getElementById('topicPieChart')) {
    const fetchStats = async () => {
        try {
            const response = await fetch('/api/statistics');
            const stats = await response.json();
            
            // Topic Pie Chart
            const topicCtx = document.getElementById('topicPieChart').getContext('2d');
            new Chart(topicCtx, {
                type: 'doughnut',
                data: {
                    labels: stats.problems_per_topic.map(t => t.topic),
                    datasets: [{
                        data: stats.problems_per_topic.map(t => t.count),
                        backgroundColor: [
                            '#0d6efd', '#6610f2', '#6f42c1', '#d63384', '#dc3545', 
                            '#fd7e14', '#ffc107', '#198754', '#20c997', '#0dcaf0'
                        ]
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });

            // Difficulty Bar Chart
            const diffCtx = document.getElementById('difficultyBarChart').getContext('2d');
            
            // Fixed order for difficulties
            const diffOrder = ['Very Easy', 'Easy', 'Medium', 'Medium Hard', 'Hard', 'Expert'];
            const diffData = diffOrder.map(d => {
                const found = stats.problems_per_difficulty.find(x => x.difficulty === d);
                return found ? found.count : 0;
            });
            
            new Chart(diffCtx, {
                type: 'bar',
                data: {
                    labels: diffOrder,
                    datasets: [{
                        label: 'Problems',
                        data: diffData,
                        backgroundColor: [
                            '#0d6efd', '#198754', '#ffc107', '#fd7e14', '#dc3545', '#6610f2'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: { y: { beginAtZero: true } }
                }
            });

            // Top 10 Topics Bar Chart
            const topTopicsCtx = document.getElementById('topTopicsBarChart').getContext('2d');
            const top10 = stats.problems_per_topic.slice(0, 10);
            new Chart(topTopicsCtx, {
                type: 'bar',
                data: {
                    labels: top10.map(t => t.topic),
                    datasets: [{
                        label: 'Problems',
                        data: top10.map(t => t.count),
                        backgroundColor: '#0dcaf0'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: { y: { beginAtZero: true } }
                }
            });

        } catch (error) {
            console.error('Error fetching statistics:', error);
        }
    };

    fetchStats();
}
