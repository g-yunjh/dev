document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('hanjaForm');
    const resultSection = document.getElementById('resultSection');
    const resultTableBody = document.querySelector('#resultTable tbody');
    const copyButton = document.getElementById('copyButton');
    const downloadButton = document.getElementById('downloadButton');
    const MAX_LENGTH = 10000;

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const hanjaInput = document.getElementById('hanjaInput').value.trim();

        if (hanjaInput.length > MAX_LENGTH) {
            alert(`입력한 한자가 너무 많습니다. 최대 ${MAX_LENGTH}자까지 입력할 수 있습니다.`);
            return;
        }

        if (!hanjaInput) {
            alert('한자를 입력해 주세요.');
            return;
        }

        try {
            const response = await fetch('/process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ hanja: hanjaInput })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok.');
            }

            const data = await response.json();

            // Clear previous results
            resultTableBody.innerHTML = '';

            // Populate table with new results
            data.forEach(item => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td class="hanja-col">${item.hanja}</td>
                    <td>${item.meaning}</td>
                `;
                resultTableBody.appendChild(row);
            });

            // Show the result section
            resultSection.classList.remove('hidden');
        } catch (error) {
            console.error('Fetch error:', error);
        }
    });

    copyButton.addEventListener('click', () => {
        const rows = Array.from(resultTableBody.querySelectorAll('tr')).map(row => {
            const cells = Array.from(row.querySelectorAll('td')).map(cell => cell.textContent).join('\t');
            return cells;
        }).join('\n');
        
        navigator.clipboard.writeText(rows).then(() => {
            alert('내용이 클립보드에 복사되었습니다.');
        });
    });

    downloadButton.addEventListener('click', () => {
        const rows = Array.from(resultTableBody.querySelectorAll('tr')).map(row => {
            const cells = Array.from(row.querySelectorAll('td')).map(cell => cell.textContent).join('\t');
            return cells;
        }).join('\n');
        
        const blob = new Blob([rows], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'results.txt';
        a.click();
        URL.revokeObjectURL(url);
    });
});