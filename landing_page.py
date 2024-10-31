landing_page = """
<!DOCTYPE html>
<html>
<head>
    <title>Debate Search</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <style>
        .main-container {
            height: 100vh;
            overflow-y: auto;
        }

        .search-container {
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        .results-container {
            min-height: 100vh;
            opacity: 0;
            transition: opacity 0.5s ease-in-out;
            display: none;
            position: relative;
        }

        .results-container.show {
            opacity: 1;
            display: block;
        }

        .column {
            transition: all 0.5s ease-in-out;
            opacity: 0;
            transform: translateX(-20px);
        }

        .column.show {
            opacity: 1;
            transform: translateX(0);
        }

        .search-result {
            animation: fadeIn 0.5s ease-in-out forwards;
            opacity: 0;
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .loading-dot {
            animation: loadingDot 1.4s infinite;
        }

        .loading-dot:nth-child(2) {
            animation-delay: 0.2s;
        }

        .loading-dot:nth-child(3) {
            animation-delay: 0.4s;
        }

        .modal {
            transition: opacity 0.3s ease-in-out;
        }
        
        .modal-content {
            transform: scale(0.95);
            transition: transform 0.3s ease-in-out;
        }
        
        .modal.show .modal-content {
            transform: scale(1);
        }
        
        .settings-button {
            transition: transform 0.2s ease-in-out;
        }
        
        .settings-button:hover {
            transform: rotate(45deg);
        }

        @keyframes loadingDot {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1.0); }
        }

        html {
            scroll-behavior: smooth;
        }
    </style>
</head>
<body>
    <div class="main-container">
    <!-- Settings Button -->
        <button id="settings-btn" 
                class="settings-button fixed top-4 right-4 p-2 bg-white rounded-full shadow-lg hover:bg-gray-50 focus:outline-none">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
        </button>

        <!-- Settings Modal -->
        <div id="settings-modal" class="modal fixed inset-0 bg-black bg-opacity-50 hidden flex items-center justify-center z-50">
            <div class="modal-content bg-white rounded-lg w-full max-w-md mx-4">
                <div class="p-6">
                    <div class="flex justify-between items-center mb-6">
                        <h2 class="text-2xl font-bold text-gray-800">设置</h2>
                        <button id="close-settings" class="text-gray-600 hover:text-gray-800">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                        </button>
                    </div>
                    
                    <div class="space-y-6">
                        <!-- Search Engine Selection -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">搜索引擎</label>
                            <select id="search-engine" class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                                <option value="searxng">SearxNG</option>
                                <option value="duckduckgo">DuckDuckGo</option>
                            </select>
                        </div>

                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">搜索url</label>
                            <input type="text" id="search-url" 
                                   class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                        </div>

                        <!-- OpenAI API Key -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">OpenAI API Key</label>
                            <input type="password" id="api-key" 
                                   class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                        </div>

                        <!-- OpenAI Base URL -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">OpenAI Base URL</label>
                            <input type="text" id="base-url" 
                                   class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                        </div>

                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">模型</label>
                            <select id="model" class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                                <option value="gpt-4o-mini">gpt-4o-mini</option>
                                <option value="gpt-4-turbo">gpt-4-turbo</option>
                                <option value="gemini-1.5-flash">gemini-1.5-flash</option>
                            </select>
                        </div>

                        <!-- Save Button -->
                        <button id="save-settings" 
                                class="w-full bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors">
                            保存设置
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <div class="search-container flex flex-col items-center justify-center p-4" id="search-section">
            <div class="w-full max-w-2xl text-center mb-8">
                <h1 class="text-4xl font-bold mb-4 text-gray-800">Debate Search</h1>
                <p class="text-gray-600">输入话题，探索正反两面的观点</p>
            </div>
            <div class="w-full max-w-2xl">
                <div class="bg-white rounded-full shadow-lg flex items-center p-4">
                    <input type="text" id="search-input"
                        class="flex-1 outline-none text-lg px-4"
                        placeholder="输入你想探索的话题..."
                        autocomplete="off">
                    <button onclick="startSearch()"
                        class="bg-blue-500 text-white px-6 py-2 rounded-full hover:bg-blue-600 transition-colors">
                        搜索
                    </button>
                </div>
            </div>
        </div>

        <div class="results-container" id="results-section">
            <div class="flex flex-col md:flex-row min-h-screen">
                <div class="column flex-1 p-6 bg-green-50" id="positive-column">
                    <h2 class="text-2xl font-bold mb-6 text-green-800">支持观点</h2>
                    <div id="positive-results" class="space-y-4"></div>
                </div>
                <div class="column flex-1 p-6 bg-red-50" id="negative-column">
                    <h2 class="text-2xl font-bold mb-6 text-red-800">反对观点</h2>
                    <div id="negative-results" class="space-y-4"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const ws = new WebSocket("ws://localhost:8000/ws");
        let currentColumn = null;
        let currentMessageElement = null;
        let scrollTimeout = null;

        function showLoading(element) {
            const loading = document.createElement("div");
            loading.className = "flex justify-center space-x-2 my-4";
            loading.innerHTML = `
                <div class="loading-dot w-3 h-3 bg-gray-500 rounded-full"></div>
                <div class="loading-dot w-3 h-3 bg-gray-500 rounded-full"></div>
                <div class="loading-dot w-3 h-3 bg-gray-500 rounded-full"></div>
            `;
            element.appendChild(loading);
            return loading;
        }

        function scrollToResults() {
            const resultsSection = document.getElementById('results-section');
            if (resultsSection) {
                resultsSection.scrollIntoView({ behavior: 'smooth' });
            }
        }

        function startSearch() {
            const query = document.getElementById('search-input').value.trim();
            if (!query) return;

            // 显示结果视图
            const resultsView = document.querySelector('.results-container');
            resultsView.classList.add('show');
            
            // 设置延时滚动，等待结果容器显示完成
            setTimeout(scrollToResults, 100);

            // 清空之前的结果
            document.getElementById('positive-results').innerHTML = '';
            document.getElementById('negative-results').innerHTML = '';

            // 添加加载动画
            const posLoading = showLoading(document.getElementById('positive-results'));
            const negLoading = showLoading(document.getElementById('negative-results'));

            // 显示列
            document.getElementById('positive-column').classList.add('show');
            document.getElementById('negative-column').classList.add('show');

            // 发送查询
            ws.send(JSON.stringify({ type: "search", message: query }));
        }

        // 监听滚动事件，防止可能的回弹
        document.addEventListener('scroll', () => {
            if (scrollTimeout) {
                clearTimeout(scrollTimeout);
            }
        });

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);

            if (data.type === 'keywords') {
                const posResults = document.getElementById('positive-results');
                const negResults = document.getElementById('negative-results');
                posResults.innerHTML = '';
                negResults.innerHTML = '';

                // 显示关键词
                const posKeywords = document.createElement('div');
                posKeywords.className = 'search-result bg-white rounded-lg p-4 shadow mb-4';
                posKeywords.innerHTML = `<h3 class="font-bold">搜索关键词:</h3><p>${data.positive.join(', ')}</p>`;
                posResults.appendChild(posKeywords);

                const negKeywords = document.createElement('div');
                negKeywords.className = 'search-result bg-white rounded-lg p-4 shadow mb-4';
                negKeywords.innerHTML = `<h3 class="font-bold">搜索关键词:</h3><p>${data.negative.join(', ')}</p>`;
                negResults.appendChild(negKeywords);
            }

            if (data.type === 'result') {
                const targetDiv = data.perspective === 'positive' ?
                    document.getElementById('positive-results') :
                    document.getElementById('negative-results');

                const resultElement = document.createElement('div');
                resultElement.className = 'search-result bg-white rounded-lg p-4 shadow';
                resultElement.innerHTML = `
                    <h3 class="font-bold text-lg mb-2">${data.title}</h3>
                    <p class="text-gray-600">${data.content}</p>
                    <div class="text-sm text-gray-400 mt-2">来源: ${data.source}</div>
                `;

                targetDiv.appendChild(resultElement);
            }
        };

        // 添加回车搜索功能
        document.getElementById('search-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                startSearch();
            }
        });
        
        const settingsBtn = document.getElementById('settings-btn');
        const settingsModal = document.getElementById('settings-modal');
        const closeSettings = document.getElementById('close-settings');
        const saveSettings = document.getElementById('save-settings');
        const searchEngineSelect = document.getElementById('search-engine');
        const searchUrl = document.getElementById('search-url');
        const apiKeyInput = document.getElementById('api-key');
        const baseUrlInput = document.getElementById('base-url');
        const modelInput = document.getElementById('model');

        // Load saved settings
        function loadSettings() {
            const settings = JSON.parse(localStorage.getItem('debateSearchSettings') || '{}');
            searchEngineSelect.value = settings.searchEngine || 'searxng';
            searchUrl.value = settings.searchUrl || 'http://192.168.31.2:8080/search?q=';
            apiKeyInput.value = settings.apiKey || '';
            baseUrlInput.value = settings.baseUrl || '';
            modelInput.value = settings.model || 'gpt-4o-mini';
        }

        // Save settings
        function saveSettingsToStorage() {
            const settings = {
                searchEngine: searchEngineSelect.value,
                searchUrl: searchUrl.value,
                apiKey: apiKeyInput.value,
                baseUrl: baseUrlInput.value,
                model: modelInput.value
            };
            localStorage.setItem('debateSearchSettings', JSON.stringify(settings));
            
            // Send settings update to server
            ws.send(JSON.stringify({
                type: "settings_update",
                settings: settings
            }));

            // Close modal
            settingsModal.classList.remove('show');
            settingsModal.classList.add('hidden');
        }

        // Event Listeners
        settingsBtn.addEventListener('click', () => {
            settingsModal.classList.remove('hidden');
            setTimeout(() => settingsModal.classList.add('show'), 10);
        });

        closeSettings.addEventListener('click', () => {
            settingsModal.classList.remove('show');
            setTimeout(() => settingsModal.classList.add('hidden'), 300);
        });

        saveSettings.addEventListener('click', saveSettingsToStorage);

        // Close modal when clicking outside
        settingsModal.addEventListener('click', (e) => {
            if (e.target === settingsModal) {
                settingsModal.classList.remove('show');
                setTimeout(() => settingsModal.classList.add('hidden'), 300);
            }
        });

        // Load settings on page load
        document.addEventListener('DOMContentLoaded', loadSettings);

        // Update the startSearch function to include the selected search engine
        function startSearch() {
            const query = document.getElementById('search-input').value.trim();
            if (!query) return;

            const settings = JSON.parse(localStorage.getItem('debateSearchSettings') || '{}');

            // 显示结果视图
            const resultsView = document.querySelector('.results-container');
            resultsView.classList.add('show');
            
            // 设置延时滚动，等待结果容器显示完成
            setTimeout(scrollToResults, 100);

            // 清空之前的结果
            document.getElementById('positive-results').innerHTML = '';
            document.getElementById('negative-results').innerHTML = '';

            // 添加加载动画
            const posLoading = showLoading(document.getElementById('positive-results'));
            const negLoading = showLoading(document.getElementById('negative-results'));

            // 显示列
            document.getElementById('positive-column').classList.add('show');
            document.getElementById('negative-column').classList.add('show');

            // 发送查询
            ws.send(JSON.stringify({ 
                type: "search", 
                message: query,
                searchEngine: settings.searchEngine || 'searxng'
            }));
        }

        // 监听滚动事件，防止可能的回弹
        document.addEventListener('scroll', () => {
            if (scrollTimeout) {
                clearTimeout(scrollTimeout);
            }
        });

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);

            if (data.type === 'keywords') {
                const posResults = document.getElementById('positive-results');
                const negResults = document.getElementById('negative-results');
                posResults.innerHTML = '';
                negResults.innerHTML = '';

                // 显示关键词
                const posKeywords = document.createElement('div');
                posKeywords.className = 'search-result bg-white rounded-lg p-4 shadow mb-4';
                posKeywords.innerHTML = `<h3 class="font-bold">搜索关键词:</h3><p>${data.positive.join(', ')}</p>`;
                posResults.appendChild(posKeywords);

                const negKeywords = document.createElement('div');
                negKeywords.className = 'search-result bg-white rounded-lg p-4 shadow mb-4';
                negKeywords.innerHTML = `<h3 class="font-bold">搜索关键词:</h3><p>${data.negative.join(', ')}</p>`;
                negResults.appendChild(negKeywords);
            }

            if (data.type === 'result') {
                const targetDiv = data.perspective === 'positive' ?
                    document.getElementById('positive-results') :
                    document.getElementById('negative-results');

                const resultElement = document.createElement('div');
                resultElement.className = 'search-result bg-white rounded-lg p-4 shadow';
                resultElement.innerHTML = `
                    <h3 class="font-bold text-lg mb-2">${data.title}</h3>
                    <p class="text-gray-600">${data.content}</p>
                    <div class="text-sm text-gray-400 mt-2">来源: ${data.source}</div>
                `;

                targetDiv.appendChild(resultElement);
            }
        };
    </script>
</body>
</html>
"""