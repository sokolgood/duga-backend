class TagsManager {
    constructor(inputId, listId, hiddenId, isCategory = false) {
        this.input = document.getElementById(inputId);
        this.list = document.getElementById(listId);
        this.hidden = document.getElementById(hiddenId);
        this.isCategory = isCategory;
        this.tags = new Set();

        this.setupInput();
        this.setupSortable();
        this.loadExistingTags();
    }

    setupInput() {
        this.input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ',') {
                e.preventDefault();
                this.addTag();
            }
            else if (e.key === 'Backspace' && this.input.value === '') {
                const lastTag = this.list.lastElementChild;
                if (lastTag) {
                    const value = lastTag.querySelector('span').textContent;
                    // this.removeTag(lastTag, value);
                    setTimeout(() => this.removeTag(lastTag, value), 0);
                }
            }
        });

        this.input.addEventListener('blur', () => {
            if (this.input.value) {
                this.addTag();
            }
        });
    }

    setupSortable() {
        new Sortable(this.list, {
            animation: 150,
            onEnd: () => {
                this.updateHiddenInput();
            }
        });
    }

    loadExistingTags() {
        if (this.hidden.value) {
            const tags = this.hidden.value.split(',');
            tags.forEach(tag => {
                if (tag) {
                    this.tags.add(tag.trim());
                    this.createTagElement(tag.trim());
                }
            });
        }
    }

    addTag() {
        const value = this.input.value.trim();
        if (value && !this.tags.has(value)) {
            this.tags.add(value);
            this.createTagElement(value);
            this.updateHiddenInput();
        }
        this.input.value = '';
    }

    createTagElement(value) {
        const tag = document.createElement('div');
        tag.className = this.isCategory ? 'category-item' : 'tag-item';

        const text = document.createElement('span');
        text.textContent = value;
        tag.appendChild(text);

        const deleteBtn = document.createElement('button');
        deleteBtn.type = 'button';
        deleteBtn.className = 'delete-tag';
        deleteBtn.innerHTML = '×';
        deleteBtn.onclick = (e) => {
            e.stopPropagation();
            this.removeTag(tag, value);
        };
        tag.appendChild(deleteBtn);

        this.list.appendChild(tag);
    }

    removeTag(element, value) {
        element.remove();
        this.tags.delete(value);
        this.updateHiddenInput();
    }

    updateHiddenInput() {
        const tags = Array.from(this.list.children)
            .map(tag => tag.querySelector('span').textContent);
        this.hidden.value = tags.join(',');
    }
}
