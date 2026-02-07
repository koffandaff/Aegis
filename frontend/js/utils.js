class Utils {
    static escapeHtml(text) {
        if (!text) return "";
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    static formatBytes(bytes, decimals = 2) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }

    static showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = typeof message === 'object' ? JSON.stringify(message) : message;

        container.appendChild(toast);

        // Trigger reflow
        toast.offsetHeight;

        // Remove after 3 seconds
        setTimeout(() => {
            toast.style.animation = 'slideIn 0.3s ease reverse forwards';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    static formatJSON(json) {
        if (typeof json !== 'string') {
            json = JSON.stringify(json, undefined, 2);
        }

        json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
            let cls = 'number';
            if (/^"/.test(match)) {
                if (/:$/.test(match)) {
                    cls = 'key';
                } else {
                    cls = 'string';
                }
            } else if (/true|false/.test(match)) {
                cls = 'boolean';
            } else if (/null/.test(match)) {
                cls = 'null';
            }
            return '<span class="' + cls + '">' + match + '</span>';
        });
    }

    static parseDate(isoString) {
        if (!isoString) return 'N/A';
        try {
            return new Date(isoString).toLocaleString();
        } catch (e) {
            return 'Invalid Date';
        }
    }

    static renderMarkdown(text) {
        if (!text) return "";
        return text
            .replace(/^#### (.*)$/gm, '<h4 style="color: var(--primary); margin-bottom: 0.5rem; margin-top: 1.5rem; font-weight: bold;">$1</h4>')
            .replace(/^### (.*)$/gm, '<h3 style="color: var(--secondary); margin-bottom: 1rem; margin-top: 0.5rem; border-bottom: 1px solid rgba(0,255,157,0.1); padding-bottom: 0.5rem;">$1</h3>')
            .replace(/^## (.*)$/gm, '<h2 style="color: var(--primary); margin-bottom: 1.2rem; margin-top: 2rem; border-bottom: 2px solid var(--primary); padding-bottom: 0.5rem;">$1</h2>')
            .replace(/^# (.*)$/gm, '<h1 style="color: var(--primary); margin-bottom: 1.5rem; margin-top: 2.5rem; text-align: center; border-bottom: 2px solid var(--secondary); padding-bottom: 0.8rem;">$1</h1>')
            .replace(/\*\*(.*)\*\*/g, '<strong style="color: var(--primary);">$1</strong>')
            .replace(/^- (.*)$/gm, '<li style="margin-left: 1.5rem; margin-bottom: 0.4rem; color: var(--text-main); list-style-type: disc;">$1</li>')
            .replace(/`(.*)`/g, '<code style="background: rgba(0,255,157,0.1); padding: 2px 6px; border-radius: 4px; color: var(--primary); font-family: \'JetBrains Mono\';">$1</code>')
            .replace(/\n/g, '<br>');
    }

    static generateId(length = 8) {
        return Math.random().toString(36).substring(2, 2 + length);
    }

    static async visualizeProgress(id, duration, steps) {
        const bar = document.getElementById(`${id}-bar`);
        const text = document.getElementById(`${id}-text`);
        const container = document.getElementById(`${id}-container`);

        container.style.display = 'block';
        text.style.display = 'block';
        bar.style.width = '0%';

        const interval = duration / 100;
        let progress = 0;
        let stepIdx = 0;

        return new Promise(resolve => {
            const timer = setInterval(() => {
                progress += 1;
                bar.style.width = `${progress}%`;

                // Update text based on progress milestones
                if (steps && steps.length > 0) {
                    if (progress > ((stepIdx + 1) * (100 / steps.length))) {
                        stepIdx++;
                        if (stepIdx < steps.length) {
                            text.textContent = steps[stepIdx];
                        }
                    } else if (stepIdx === 0 && progress < (100 / steps.length)) {
                        text.textContent = steps[0];
                    }
                }

                if (progress >= 100) {
                    clearInterval(timer);
                    setTimeout(resolve, 300);
                }
            }, interval);
        });
    static maskIP(ip) {
        if (!ip) return '0.0.0.0';
        if (ip.includes(':')) { // IPv6
            const parts = ip.split(':');
            return `${parts[0]}:****:****:${parts[parts.length - 1]}`;
        }
        const parts = ip.split('.');
        if (parts.length === 4) {
            return `${parts[0]}.***.***.${parts[3]}`;
        }
        return ip;
    }
}

export default Utils;
