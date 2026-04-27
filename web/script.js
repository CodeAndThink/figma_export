document.addEventListener('DOMContentLoaded', () => {
    const exportBtn = document.getElementById('exportBtn');
    const backBtn = document.getElementById('backBtn');
    const logOutput = document.getElementById('logOutput');
    const screenGrid = document.getElementById('screenGrid');

    const screenConfig = document.getElementById('screenConfig');
    const screenProcess = document.getElementById('screenProcess');
    const screenResults = document.getElementById('screenResults');

    const detailModal = document.getElementById('detailModal');
    const closeModal = document.getElementById('closeModal');
    const modalImg = document.getElementById('modalImg');
    const modalJson = document.getElementById('modalJson');
    const hoverOverlay = document.getElementById('hoverOverlay');

    let currentNodes = [];
    let rootBox = null;
    let rootNodeId = null;
    let nodeToLines = {};
    let lastHitNode = null;
    let isLocked = false;

    function showScreen(screenId) {
        [screenConfig, screenProcess, screenResults].forEach(s => s.classList.add('hidden'));
        document.getElementById(screenId).classList.remove('hidden');
    }

    exportBtn.addEventListener('click', async () => {
        const token = document.getElementById('token').value.trim();
        const fileLink = document.getElementById('fileLink').value.trim();
        if (!token || !fileLink) {
            alert('Vui lòng nhập đầy đủ Token và Link Figma!');
            return;
        }

        showScreen('screenProcess');
        logOutput.innerHTML = '[*] Đang khởi động quá trình export...<br>';
        updateStep(1, 'active');
        updateStep(2, '');
        updateStep(3, '');

        try {
            const response = await fetch('/api/export', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token, file_link: fileLink })
            });

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                const text = decoder.decode(value);
                const lines = text.split('\n');
                lines.forEach(line => {
                    if (!line.trim()) return;
                    logOutput.innerHTML += line + '<br>';
                    logOutput.scrollTop = logOutput.scrollHeight;
                    if (line.includes('[1/3]')) updateStep(1, 'active');
                    if (line.includes('[2/3]')) { updateStep(1, 'done'); updateStep(2, 'active'); }
                    if (line.includes('[3/3]')) { updateStep(2, 'done'); updateStep(3, 'active'); }
                    if (line.includes('=== HOAN THANH')) {
                        updateStep(3, 'done');
                        setTimeout(() => showResults(), 1000);
                    }
                });
            }
        } catch (err) {
            logOutput.innerHTML += `<span style="color: red;">[ERROR] Lỗi kết nối: ${err.message}</span><br>`;
        }
    });

    backBtn.addEventListener('click', () => showScreen('screenConfig'));
    closeModal.addEventListener('click', () => detailModal.classList.add('hidden'));
    
    // Đóng modal khi nhấn vào overlay mờ
    detailModal.querySelector('.modal-overlay').addEventListener('click', () => detailModal.classList.add('hidden'));

    // BỎ CHỌN khi nhấn vào vùng trống trong modal (trừ ảnh và code)
    detailModal.addEventListener('click', (e) => {
        // Nếu click trúng vào modal-body hoặc modal-left (phần nền đen) nhưng không trúng ảnh
        if (e.target.classList.contains('modal-body') || 
            e.target.classList.contains('modal-left') || 
            e.target.classList.contains('img-container')) {
            unlockHighlight();
        }
    });

    function unlockHighlight() {
        isLocked = false;
        hoverOverlay.style.borderColor = 'var(--secondary)';
        hoverOverlay.style.boxShadow = '0 0 15px var(--secondary)';
        document.querySelectorAll('.json-line.highlight').forEach(el => el.classList.remove('highlight'));
    }

    function updateStep(stepNum, status) {
        const el = document.getElementById(`step${stepNum}`);
        if (el) el.className = 'step ' + status;
    }

    async function showResults() {
        showScreen('screenResults');
        screenGrid.innerHTML = '';
        try {
            const res = await fetch('/api/screens');
            const folders = await res.json();
            folders.forEach(folder => {
                const item = document.createElement('div');
                item.className = 'screen-item';
                item.style.cursor = 'pointer';
                item.innerHTML = `
                    <img src="/api/preview/${folder}" alt="${folder}" onerror="this.src='https://via.placeholder.com/140x250?text=No+Preview'">
                    <p title="${folder}">${folder}</p>
                `;
                item.addEventListener('click', () => openDetail(folder));
                screenGrid.appendChild(item);
            });
        } catch (err) { console.error('Lỗi khi tải:', err); }
    }

    async function openDetail(folder) {
        detailModal.classList.remove('hidden');
        modalImg.src = `/api/preview/${folder}`;
        modalJson.innerHTML = 'Đang tải dữ liệu...';
        hoverOverlay.style.display = 'none';
        lastHitNode = null;
        isLocked = false;
        
        try {
            const res = await fetch(`/api/data/${folder}`);
            const data = await res.json();
            processFigmaData(data);
            renderJsonWithLines(data);
        } catch (err) { modalJson.textContent = 'Lỗi tải JSON'; }
    }

    function processFigmaData(data) {
        currentNodes = [];
        rootBox = data.absoluteBoundingBox;
        rootNodeId = data.id;
        function traverse(node) {
            if (node.absoluteBoundingBox) {
                currentNodes.push({
                    id: node.id,
                    name: node.name,
                    box: node.absoluteBoundingBox
                });
            }
            if (node.children) node.children.forEach(traverse);
        }
        traverse(data);
        currentNodes.sort((a, b) => (a.box.width * a.box.height) - (b.box.width * b.box.height));
    }

    function renderJsonWithLines(data) {
        const jsonStr = JSON.stringify(data, null, 4);
        const lines = jsonStr.split('\n');
        nodeToLines = {};
        lines.forEach((line, index) => {
            currentNodes.forEach(node => {
                if (line.includes(`"id": "${node.id}"`)) {
                    nodeToLines[node.id] = index;
                }
            });
        });
        modalJson.innerHTML = lines.map((line, i) => `<span class="json-line" id="line-${i}">${escapeHtml(line)}</span>`).join('');
    }

    modalImg.addEventListener('mousemove', (e) => {
        if (!rootBox || isLocked) return;

        const x = e.offsetX;
        const y = e.offsetY;
        const w = modalImg.clientWidth;
        const h = modalImg.clientHeight;

        const scaleX = rootBox.width / w;
        const scaleY = rootBox.height / h;

        const figmaX = rootBox.x + (x * scaleX);
        const figmaY = rootBox.y + (y * scaleY);

        const hit = currentNodes.find(node => {
            const b = node.box;
            return figmaX >= b.x && figmaX <= b.x + b.width &&
                   figmaY >= b.y && figmaY <= b.y + b.height;
        });

        if (hit) {
            lastHitNode = hit;
            updateOverlayPosition(hit, scaleX, scaleY);
        } else {
            lastHitNode = null;
            hoverOverlay.style.display = 'none';
        }
    });

    modalImg.addEventListener('click', (e) => {
        e.stopPropagation(); // Ngăn sự kiện Click lan ra lớp modal bên ngoài
        if (lastHitNode) {
            if (lastHitNode.id === rootNodeId) {
                unlockHighlight();
            } else {
                isLocked = true;
                highlightJsonNode(lastHitNode.id);
                hoverOverlay.style.borderColor = '#00ff88'; 
                hoverOverlay.style.boxShadow = '0 0 20px #00ff88';
            }
        }
    });

    function updateOverlayPosition(node, scaleX, scaleY) {
        hoverOverlay.style.display = 'block';
        hoverOverlay.style.left = `${(node.box.x - rootBox.x) / scaleX}px`;
        hoverOverlay.style.top = `${(node.box.y - rootBox.y) / scaleY}px`;
        hoverOverlay.style.width = `${node.box.width / scaleX}px`;
        hoverOverlay.style.height = `${node.box.height / scaleY}px`;
    }

    function highlightJsonNode(nodeId) {
        document.querySelectorAll('.json-line.highlight').forEach(el => el.classList.remove('highlight'));
        const lineIndex = nodeToLines[nodeId];
        if (lineIndex !== undefined) {
            const lineEl = document.getElementById(`line-${lineIndex}`);
            if (lineEl) {
                lineEl.classList.add('highlight');
                lineEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});
