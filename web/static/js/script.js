document.addEventListener('DOMContentLoaded', () => {
    const menuToggle = document.getElementById('menu-toggle');
    const menuClose = document.getElementById('menu-close');
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.querySelector('.overlay');

    function toggleMenu() {
        sidebar.classList.toggle('active');
        overlay.classList.toggle('active');
    }

    if (menuToggle) {
        menuToggle.addEventListener('click', toggleMenu);
    }

    if (menuClose) {
        menuClose.addEventListener('click', () => {
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
        });
    }

    if (overlay) {
        overlay.addEventListener('click', toggleMenu);
    }

    // Close menu when a link is clicked (using event delegation)
    document.addEventListener('click', (e) => {
        const link = e.target.closest('.nav-link');
        if (link && sidebar.classList.contains('active')) {
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
        }
    });

    // Theme Switch
    const toggleSwitch = document.querySelector('.theme-switch input[type="checkbox"]');
    const currentTheme = localStorage.getItem('theme');

    if (currentTheme) {
        document.documentElement.setAttribute('data-theme', currentTheme);
        if (currentTheme === 'dark') {
            toggleSwitch.checked = true;
        }
    }

    function switchTheme(e) {
        if (e.target.checked) {
            document.documentElement.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', 'dark');
        } else {
            document.documentElement.setAttribute('data-theme', 'light');
            localStorage.setItem('theme', 'light');
        }
    }

    if (toggleSwitch) {
        toggleSwitch.addEventListener('change', switchTheme, false);
    }

    // Auto-close sidebar on mouse leave
    sidebar.addEventListener('mouseleave', () => {
        if (sidebar.classList.contains('active')) {
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
        }
    });

    // --- Bug Detection Logic ---
    const analyzeBtn = document.getElementById('analyze-btn');
    const codeInput = document.getElementById('code-input');
    const resultsArea = document.getElementById('results-area');
    const resultsContent = document.getElementById('results-content');

    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', async () => {
            const code = codeInput.value.trim();
            if (!code) {
                alert("Please enter some code to analyze.");
                return;
            }

            // UI Loading State
            analyzeBtn.textContent = 'Analyzing...';
            analyzeBtn.disabled = true;
            resultsArea.style.display = 'none';

            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ code: code })
                });

                const data = await response.json();

                if (response.ok) {
                    resultsContent.textContent = data.result;
                    resultsArea.style.display = 'block';
                } else {
                    alert("Error: " + (data.error || "Unknown error occurred"));
                }

            } catch (error) {
                console.error('Error:', error);
                alert("Failed to connect to the server.");
            } finally {
                // Reset UI State
                analyzeBtn.textContent = 'Analyze Code';
                analyzeBtn.disabled = false;
            }
        });
    }

    // --- 1. Hero Typewriter Effect ---
    const words = ["Python", "Java"];
    let i = 0;
    let timer;

    function typingEffect() {
        const word = words[i];
        const element = document.querySelector('.typewriter-text');
        if (!element) return;

        let currentText = element.textContent;
        let isDeleting = false;

        // This is a simplified version. For full effect we'd implement character-by-character backspacing
        // reusing a simple interval for rotation for now to keep it lightweight
        setInterval(() => {
            i = (i + 1) % words.length;
            element.style.opacity = 0;
            setTimeout(() => {
                element.textContent = words[i];
                element.style.opacity = 1;
            }, 500);
        }, 3000);
    }

    // Simple CSS transition-based fade for typewriter
    const typeWriterEl = document.querySelector('.typewriter-text');
    if (typeWriterEl) {
        typeWriterEl.style.transition = "opacity 0.5s ease";
        typingEffect();
    }


    // --- 2. Live Code Demo Terminal ---
    const terminalCode = document.getElementById('terminal-code');
    const terminalTitle = document.querySelector('.terminal-title');
    const tabs = document.querySelectorAll('.lang-tab');

    // Snippets Database
    const snippets = {
        python: {
            filename: 'demo.py',
            bug: `def calculate_area(radius):
    # Bug: using diameter formula
    return 3.14 * radius * 2`,
            fix: `def calculate_area(radius):
    # Fix: using area formula
    return 3.14 * (radius ** 2)`
        },
        java: {
            filename: 'Main.java',
            bug: `int[] numbers = {1, 2, 3};
// Bug: Accessing invalid index
System.out.println(numbers[3]);`,
            fix: `int[] numbers = {1, 2, 3};
// Fix: Correct index access
System.out.println(numbers[2]);`
        }
    };

    let currentLang = 'python';
    let charIndex = 0;
    let isFixing = false;
    let animationTimeout;
    let isPaused = false;

    if (terminalCode) {

        function typeCode() {
            if (isPaused) return;

            const currentSnippet = isFixing ? snippets[currentLang].fix : snippets[currentLang].bug;

            if (charIndex < currentSnippet.length) {
                terminalCode.textContent += currentSnippet.charAt(charIndex);
                charIndex++;
                animationTimeout = setTimeout(typeCode, 50);
            } else {
                // Text finished typing
                if (!isFixing) {
                    // Pause then fix
                    animationTimeout = setTimeout(() => {
                        isFixing = true;
                        terminalCode.textContent = "";
                        charIndex = 0;
                        typeCode();
                    }, 2000);
                } else {
                    // Reset loop
                    animationTimeout = setTimeout(() => {
                        isFixing = false;
                        terminalCode.textContent = "";
                        charIndex = 0;
                        typeCode();
                    }, 4000);
                }
            }
        }

        function switchLanguage(lang) {
            if (lang === currentLang) return; // No change

            // Update State
            currentLang = lang;
            isFixing = false;
            charIndex = 0;
            isPaused = false;

            // Clear current animation
            clearTimeout(animationTimeout);
            terminalCode.textContent = "";

            // Update UI
            terminalTitle.textContent = snippets[lang].filename;

            tabs.forEach(tab => {
                if (tab.dataset.lang === lang) {
                    tab.classList.add('active');
                    tab.style.color = '#fff';
                    tab.style.opacity = '1';
                    tab.style.borderBottom = '2px solid #6366f1';
                } else {
                    tab.classList.remove('active');
                    tab.style.color = '#94a3b8';
                    tab.style.opacity = '0.7';
                    tab.style.borderBottom = '2px solid transparent';
                }
            });

            // Restart Animation
            typeCode();
        }

        // Tab Event Listeners
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                switchLanguage(tab.dataset.lang);
            });
        });

        // Start initial
        typeCode();
    }


    // --- 3. Animated Stats Counters ---
    const stats = document.querySelectorAll('.stat-number');

    if (stats.length > 0) {
        const observerOptions = { threshold: 0.5 };

        const statsObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const counter = entry.target;
                    const target = +counter.getAttribute('data-target');
                    const duration = 2000; // 2 seconds
                    const increment = target / (duration / 16); // 60fps

                    let current = 0;

                    const updateCounter = () => {
                        current += increment;
                        if (current < target) {
                            counter.textContent = Math.ceil(current).toLocaleString();
                            requestAnimationFrame(updateCounter);
                        } else {
                            counter.textContent = target.toLocaleString() + (target > 100 ? '+' : '%');
                        }
                    };

                    updateCounter();
                    statsObserver.unobserve(counter);
                }
            });
        }, observerOptions);

        stats.forEach(stat => statsObserver.observe(stat));
    }
});
