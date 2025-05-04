document.addEventListener('DOMContentLoaded', function() {
    const questionForm = document.getElementById('question-form');
    const questionInput = document.getElementById('question');
    const compareMode = document.getElementById('compare-mode');
    const loadingIndicator = document.getElementById('loading');
    const resultsContainer = document.getElementById('results-container');
    const ragAnswer = document.getElementById('rag-answer');
    const referencesContainer = document.getElementById('references-container');
    const directAnswerContainer = document.getElementById('direct-answer-container');
    const directAnswer = document.getElementById('direct-answer');

    // API 端点
    const API_ENDPOINT = '/api/ask';

    // 提交问题
    questionForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const question = questionInput.value.trim();
        if (!question) {
            alert('请输入问题');
            return;
        }
        
        // 显示加载指示器
        loadingIndicator.classList.remove('d-none');
        resultsContainer.classList.add('d-none');
        
        try {
            const response = await fetch(API_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: question,
                    compare: compareMode.checked
                }),
            });
            
            if (!response.ok) {
                throw new Error('API 请求失败');
            }
            
            const data = await response.json();
            displayResults(data);
            
        } catch (error) {
            console.error('Error:', error);
            alert('处理请求时出错: ' + error.message);
        } finally {
            // 隐藏加载指示器
            loadingIndicator.classList.add('d-none');
        }
    });
    
    // 显示结果
    function displayResults(data) {
        // 显示 RAG 回答
        ragAnswer.textContent = data.rag_response.answer;
        
        // 显示参考文档
        referencesContainer.innerHTML = '';
        data.rag_response.references.forEach((ref, index) => {
            const referenceItem = document.createElement('div');
            referenceItem.className = 'reference-item';
            
            const score = Math.round(ref.score * 100) / 100;
            
            referenceItem.innerHTML = `
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <h4 class="h6 mb-0">参考文档 ${index + 1}</h4>
                    <span class="reference-score">相关度: ${score}</span>
                </div>
                <p>${formatReferenceText(ref.text)}</p>
            `;
            
            referencesContainer.appendChild(referenceItem);
        });
        
        // 显示直接 LLM 回答（如果启用了对比模式）
        if (compareMode.checked && data.direct_response) {
            directAnswer.textContent = data.direct_response.answer;
            directAnswerContainer.classList.remove('d-none');
        } else {
            directAnswerContainer.classList.add('d-none');
        }
        
        // 显示结果容器
        resultsContainer.classList.remove('d-none');
        
        // 滚动到结果
        resultsContainer.scrollIntoView({ behavior: 'smooth' });
    }
    
    // 格式化参考文本（截断长文本并突出显示关键部分）
    function formatReferenceText(text) {
        const maxLength = 300;
        if (text.length <= maxLength) {
            return text;
        }
        
        return text.substring(0, maxLength) + '...';
    }
    
    // 对比模式切换
    compareMode.addEventListener('change', function() {
        if (this.checked) {
            directAnswerContainer.classList.remove('d-none');
        } else {
            directAnswerContainer.classList.add('d-none');
        }
    });
    
    // 预填充示例问题
    const exampleQuestions = [
        "在不定期合伙的情况下，一个合伙人突然退出并清偿了其应当承担份额的合伙债务后，是否有权向其他合伙人追偿？",
        "一个公司购买了一台特种设备，该公司应该对这台设备进行哪些管理和维护措施？",
        "什么是民事诉讼？",
        "行政诉讼中被告的举证责任是什么？"
    ];
    
    questionInput.placeholder = exampleQuestions[Math.floor(Math.random() * exampleQuestions.length)];
});
